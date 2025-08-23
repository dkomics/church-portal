"""
Branch Context Management System
Handles branch selection, session management, and access control
"""
from django.shortcuts import get_object_or_404
from django.http import Http404
from functools import wraps


class BranchContextManager:
    """Manages branch context for user sessions"""
    
    SESSION_KEY = 'selected_branch_id'
    
    @classmethod
    def set_branch_context(cls, request, branch_id):
        """Set the selected branch in user session"""
        if request.user.is_authenticated:
            # Verify user has access to this branch
            if cls.user_can_access_branch(request.user, branch_id):
                request.session[cls.SESSION_KEY] = branch_id
                return True
        return False
    
    @classmethod
    def get_branch_context(cls, request):
        """Get the currently selected branch from session"""
        if request.user.is_authenticated:
            branch_id = request.session.get(cls.SESSION_KEY)
            if branch_id:
                try:
                    from membership.models import Branch
                    branch = Branch.objects.get(id=branch_id, is_active=True)
                    # Verify user still has access
                    if cls.user_can_access_branch(request.user, branch_id):
                        return branch
                    else:
                        # Remove invalid branch from session
                        cls.clear_branch_context(request)
                except Branch.DoesNotExist:
                    cls.clear_branch_context(request)
        return None
    
    @classmethod
    def clear_branch_context(cls, request):
        """Clear branch context from session"""
        if cls.SESSION_KEY in request.session:
            del request.session[cls.SESSION_KEY]
    
    @classmethod
    def user_can_access_branch(cls, user, branch_id):
        """Check if user can access the specified branch"""
        if not user.is_authenticated or not hasattr(user, 'profile'):
            return False
        
        profile = user.profile
        
        # System admin can access all branches
        if profile.is_system_admin:
            return True
        
        # Check if branch is in user's accessible branches
        try:
            from membership.models import Branch
            branch = Branch.objects.get(id=branch_id, is_active=True)
            return profile.get_accessible_branches().filter(id=branch_id).exists()
        except Branch.DoesNotExist:
            return False
    
    @classmethod
    def get_user_branch_options(cls, user):
        """Get available branch options for user"""
        if not user.is_authenticated or not hasattr(user, 'profile'):
            return []
        
        return user.profile.get_accessible_branches()


def require_branch_access(view_func):
    """
    Decorator to ensure user has access to the branch in context
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Get branch from URL parameter or session
        branch_id = request.GET.get('branch') or request.session.get(BranchContextManager.SESSION_KEY)
        
        if branch_id:
            if not BranchContextManager.user_can_access_branch(request.user, branch_id):
                raise Http404("Branch not found or access denied")
        
        return view_func(request, *args, **kwargs)
    return wrapper


def require_branch_context(view_func):
    """
    Decorator to ensure a branch is selected in context
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        branch = BranchContextManager.get_branch_context(request)
        if not branch:
            # Redirect to branch selection or home page
            from django.shortcuts import redirect
            return redirect('home')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def branch_scoped_queryset(queryset, request, branch_field='branch'):
    """
    Filter queryset to only include records from the selected branch
    """
    branch = BranchContextManager.get_branch_context(request)
    if branch:
        filter_kwargs = {branch_field: branch}
        return queryset.filter(**filter_kwargs)
    
    # If no branch context, return empty queryset for security
    return queryset.none()


def get_branch_scoped_stats(request, branch=None):
    """
    Get statistics scoped to the selected branch
    """
    from membership.models import Member
    from datetime import datetime
    
    if not branch:
        branch = BranchContextManager.get_branch_context(request)
    
    if not branch:
        return {
            'total_members': 0,
            'new_members_this_month': 0,
            'baptized_members': 0,
            'membership_class_completed': 0,
        }
    
    # Get current month for filtering
    current_month = datetime.now().replace(day=1)
    
    # Filter members by branch
    branch_members = Member.objects.filter(branch=branch)
    
    return {
        'total_members': branch_members.count(),
        'new_members_this_month': branch_members.filter(registration_date__gte=current_month).count(),
        'baptized_members': branch_members.filter(baptized='Yes').count(),
        'membership_class_completed': branch_members.filter(membership_class='Yes').count(),
    }

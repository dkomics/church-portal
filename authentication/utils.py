from django.utils import timezone
from .models import AuditLog


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """Get user agent from request"""
    return request.META.get('HTTP_USER_AGENT', '')


def log_user_action(user, action, request=None, target_member_id=None, details=None):
    """Log user action for audit trail"""
    ip_address = None
    user_agent = None
    
    if request:
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)
    
    AuditLog.objects.create(
        user=user,
        action=action,
        target_member_id=target_member_id,
        ip_address=ip_address,
        user_agent=user_agent,
        details=details or {}
    )


def require_role(allowed_roles):
    """Decorator to require specific roles for view access"""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.contrib.auth.decorators import login_required
                return login_required(view_func)(request, *args, **kwargs)
            
            if not hasattr(request.user, 'profile'):
                from django.http import HttpResponseForbidden
                return HttpResponseForbidden("Access denied: No user profile found.")
            
            if request.user.profile.role not in allowed_roles:
                from django.http import HttpResponseForbidden
                return HttpResponseForbidden("Access denied: Insufficient privileges.")
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def can_access_member_data(user, access_level='basic'):
    """Check if user can access member data at specified level"""
    if not user.is_authenticated or not hasattr(user, 'profile'):
        return False
    
    profile = user.profile
    
    if access_level == 'basic':
        return profile.role in ['secretary', 'pastor', 'admin']
    elif access_level == 'full':
        return profile.role in ['pastor', 'admin']
    elif access_level == 'admin':
        return profile.role == 'admin'
    
    return False


def filter_member_fields(member_data, user):
    """Filter member data based on user's access level"""
    if not user.is_authenticated or not hasattr(user, 'profile'):
        return {}
    
    accessible_fields = user.profile.get_accessible_member_fields()
    
    if accessible_fields == 'all':
        return member_data
    
    # Filter to only accessible fields
    filtered_data = {}
    for field in accessible_fields:
        if field in member_data:
            filtered_data[field] = member_data[field]
    
    return filtered_data

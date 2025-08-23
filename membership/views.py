from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count
from django.http import JsonResponse
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
import logging
from .models import Member, Branch, News
from .serializers import MemberSerializer
from authentication.views import can_view_directory, can_register_members
from authentication.utils import log_user_action, filter_member_fields

# Set up logging
logger = logging.getLogger(__name__)

# Custom pagination class
class MemberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

def home_page(request):
    """Home page with branch-aware statistics and features"""
    from authentication.branch_context import BranchContextManager, get_branch_scoped_stats
    
    # Handle branch reset (clear context)
    if request.GET.get('reset') == '1':
        BranchContextManager.clear_branch_context(request)
    
    # Handle branch selection from URL parameter
    selected_branch_id = request.GET.get('branch')
    if selected_branch_id:
        BranchContextManager.set_branch_context(request, selected_branch_id)
    
    # Get current branch context
    current_branch = BranchContextManager.get_branch_context(request)
    
    # Branch-scoped mode: If branch is selected, show only that branch's data
    if current_branch:
        # Get detailed single-branch statistics
        single_branch_stats = get_branch_scoped_stats(request, current_branch)
        
        # Also get aggregated overview for comparison
        aggregated_stats = get_aggregated_overview_stats(request)
        
        context = {
            'stats': single_branch_stats,
            'aggregated_stats': aggregated_stats,
            'current_branch': current_branch,
            'user_branches': [],  # Hide other branches
            'recent_news': [],
            'branch_mode': 'single',  # Indicate single-branch mode
            'show_branch_selector': False,
        }
        
        # Get branch-specific news
        try:
            context['recent_news'] = News.objects.filter(
                branch=current_branch, is_published=True
            ).order_by('-created_at')[:5]
        except:
            context['recent_news'] = []
            
    else:
        # Multi-branch mode: Show branch selector and user's accessible branches
        context = {
            'stats': {
                'total_members': 0,
                'new_members_this_month': 0,
                'baptized_members': 0,
                'membership_class_completed': 0,
            },
            'branches': [],
            'user_branches': [],
            'current_branch': None,
            'recent_news': [],
            'branch_stats': {},
            'branches_with_stats': [],  # Initialize empty for multi-branch mode
            'branch_mode': 'multi',  # Indicate multi-branch mode
            'show_branch_selector': True,
        }
        
        try:
            from django.db.models import Count
            from datetime import datetime, timedelta
            
            # Get current month for filtering
            current_month = datetime.now().replace(day=1)
            
            # Get user's accessible branches if authenticated
            if request.user.is_authenticated and hasattr(request.user, 'profile'):
                profile = request.user.profile
                context['user_branches'] = BranchContextManager.get_user_branch_options(request.user)
                
                if profile.is_system_admin:
                    members_queryset = Member.objects.all()
                else:
                    members_queryset = profile.get_accessible_members()
                
                # Calculate aggregated overview statistics across all accessible branches
                context['stats'] = {
                    'total_members': members_queryset.count(),
                    'new_members_this_month': members_queryset.filter(registration_date__gte=current_month).count(),
                    'baptized_members': members_queryset.filter(baptized='Yes').count(),
                    'membership_class_completed': members_queryset.filter(membership_class='Yes').count(),
                }
                
                # Store as aggregated stats for consistency
                context['aggregated_stats'] = context['stats']
                
                # Calculate branch-specific statistics for multi-branch view
                branches_with_stats = []
                for branch in context['user_branches']:
                    branch_members = Member.objects.filter(branch=branch)
                    branch_data = {
                        'id': branch.id,
                        'name': branch.name,
                        'code': branch.code,
                        'address': branch.address,
                        'phone': branch.phone,
                        'email': branch.email,
                        'pastor_name': branch.pastor_name,
                        'is_active': branch.is_active,
                        'total_members': branch_members.count(),
                        'new_this_month': branch_members.filter(
                            registration_date__gte=current_month
                        ).count(),
                        'baptized': branch_members.filter(baptized='Yes').count(),
                    }
                    branches_with_stats.append(branch_data)
                context['branches_with_stats'] = branches_with_stats
        except Exception as e:
            logger.warning(f"Error calculating statistics: {e}")
            # Use default empty stats if calculation fails
        
        # Get recent news (general + user's branches)
        news_queryset = News.objects.filter(
            is_published=True,
            publish_date__lte=timezone.now()
        )
        
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            if not request.user.profile.is_system_admin:
                # Filter news for user's branches
                user_branches = context['user_branches']
                news_queryset = news_queryset.filter(
                    Q(scope='general') | 
                    Q(scope='branch', branch__in=user_branches)
                )
        
        context['recent_news'] = news_queryset.order_by('-publish_date', '-priority')[:5]
    
    return render(request, 'membership/home.html', context)

def register_page(request):
    """Member registration page - accessible to all users for new member registration"""
    # Allow all users (authenticated and unauthenticated) to access registration form
    # This makes sense as new members need to register without having accounts yet
    return render(request, 'membership/register.html')

@login_required
def member_directory_page(request):
    """Member directory page - accessible to all authenticated users with role-based data filtering"""
    # Allow all authenticated users to view directory
    # Data filtering will be handled by the frontend based on user permissions
    context = {
        'user_can_view_full_details': False,
        'user_can_export_data': False,
    }
    
    # Set permissions based on user profile
    if hasattr(request.user, 'profile') and request.user.profile:
        context['user_can_view_full_details'] = request.user.profile.can_view_full_details
        context['user_can_export_data'] = request.user.profile.can_export_data
    
    return render(request, 'membership/directory.html', context)

class MemberCreateView(generics.CreateAPIView):
    """API view for creating new members - accessible to all users for new member registration"""
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = []  # Remove authentication requirement to allow new members to register
    
    def create(self, request, *args, **kwargs):
        try:
            # Log the registration attempt
            logger.info(f"New member registration attempt: {request.data.get('full_name', 'Unknown')}")
            
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                member = serializer.save()
                logger.info(f"New member registered successfully: {member.full_name} (ID: {member.membership_id})")
                
                # Return success response with member details
                return Response({
                    'success': True,
                    'message': 'Usajili umefanikiwa!',
                    'member': {
                        'membership_id': member.membership_id,
                        'full_name': member.full_name,
                        'registration_date': member.registration_date
                    }
                }, status=status.HTTP_201_CREATED)
            else:
                logger.warning(f"Member registration failed - validation errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Unexpected error during member registration: {str(e)}")
            return Response({
                'error': 'Hitilafu ya server imetokea. Tafadhali jaribu tena.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MemberListView(generics.ListAPIView):
    """API view for listing members with search and filtering - requires authentication"""
    serializer_class = MemberSerializer
    pagination_class = MemberPagination
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Member.objects.all()
        
        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search) |
                Q(membership_id__icontains=search) |
                Q(phone__icontains=search) |
                Q(email__icontains=search) |
                Q(emergency_phone__icontains=search)
            )
        
        # Filter by gender
        gender = self.request.query_params.get('gender', None)
        if gender:
            queryset = queryset.filter(gender=gender)
        
        # Filter by age category
        age_category = self.request.query_params.get('age_category', None)
        if age_category:
            queryset = queryset.filter(age_category=age_category)
        
        # Filter by membership type
        membership_type = self.request.query_params.get('membership_type', None)
        if membership_type:
            queryset = queryset.filter(membership_type=membership_type)
        
        # Filter by baptized status
        baptized = self.request.query_params.get('baptized', None)
        if baptized:
            queryset = queryset.filter(baptized=baptized)
        
        # Ordering
        ordering = self.request.query_params.get('ordering', '-registration_date')
        valid_orderings = [
            'full_name', '-full_name', 'registration_date', '-registration_date',
            'membership_id', '-membership_id', 'gender', '-gender',
            'age_category', '-age_category', 'membership_type', '-membership_type'
        ]
        if ordering in valid_orderings:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by('-registration_date')
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        try:
            response = super().list(request, *args, **kwargs)
            logger.info(f"Member list requested - returned {len(response.data.get('results', []))} members")
            return response
        except Exception as e:
            logger.error(f"Error retrieving member list: {str(e)}")
            return Response({
                'error': 'Hitilafu imetokea wakati wa kupakia orodha ya washirika.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def member_statistics(request):
    """API endpoint for member statistics"""
    try:
        current_year = timezone.now().year
        current_month = timezone.now().month
        
        stats = {
            'total_members': Member.objects.count(),
            'male_members': Member.objects.filter(gender='Male').count(),
            'female_members': Member.objects.filter(gender='Female').count(),
            'baptized_members': Member.objects.filter(baptized='Yes').count(),
            'new_members_this_year': Member.objects.filter(
                registration_date__year=current_year
            ).count(),
            'new_members_this_month': Member.objects.filter(
                registration_date__year=current_year,
                registration_date__month=current_month
            ).count(),
            'membership_class_completed': Member.objects.filter(
                membership_class='Yes'
            ).count(),
            'by_age_category': dict(
                Member.objects.values('age_category').annotate(
                    count=Count('age_category')
                ).values_list('age_category', 'count')
            ),
            'by_membership_type': dict(
                Member.objects.values('membership_type').annotate(
                    count=Count('membership_type')
                ).values_list('membership_type', 'count')
            ),
        }
        
        logger.info("Member statistics requested")
        return Response(stats)
        
    except Exception as e:
        logger.error(f"Error retrieving member statistics: {str(e)}")
        return Response({
            'error': 'Hitilafu imetokea wakati wa kupakia takwimu.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
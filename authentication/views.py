from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from .models import UserProfile, AuditLog
from .forms import UserRegistrationForm, UserProfileForm
from .utils import log_user_action, get_client_ip, get_user_agent
import json


def user_login(request):
    """Handle user login with audit logging"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                
                # Log successful login
                log_user_action(
                    user=user,
                    action='login',
                    request=request,
                    details={'login_method': 'username_password'}
                )
                
                messages.success(request, f'Karibu, {user.get_full_name() or user.username}!')
                
                # Redirect based on user role
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                
                if hasattr(user, 'profile'):
                    if user.profile.role == 'admin':
                        return redirect('authentication:admin_dashboard')
                    elif user.profile.role in ['pastor', 'secretary']:
                        return redirect('member-directory')
                    else:
                        return redirect('authentication:member_profile')
                else:
                    return redirect('home')
            else:
                messages.error(request, 'Akaunti yako haijaidhinishwa. Wasiliana na msimamizi.')
        else:
            messages.error(request, 'Jina la mtumiaji au nenosiri si sahihi.')
    
    return render(request, 'authentication/login.html')


@login_required
def user_logout(request):
    """Handle user logout with audit logging"""
    # Log logout action
    log_user_action(
        user=request.user,
        action='logout',
        request=request
    )
    
    logout(request)
    messages.success(request, 'Umetoka kikamilifu. Asante!')
    return redirect('login')


@login_required
def member_profile(request):
    """Display and allow editing of user's own profile"""
    # Get or create profile to handle cases where profile doesn't exist
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'role': 'member'}
    )
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Taarifa zako zimebadilishwa kikamilifu!')
            return redirect('member_profile')
    else:
        form = UserProfileForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile,
    }
    return render(request, 'authentication/profile.html', context)


def is_admin(user):
    """Check if user is admin"""
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.role == 'admin'


def can_manage_users(user):
    """Check if user can manage other users"""
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.can_manage_users


def can_view_directory(user):
    """Check if user can view member directory"""
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.can_view_directory


def can_register_members(user):
    """Check if user can register new members"""
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.can_register_members


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard with system overview"""
    # Get statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    recent_logins = AuditLog.objects.filter(action='login').order_by('-timestamp')[:10]
    
    # User role distribution
    role_stats = {}
    admin_count = UserProfile.objects.filter(role='admin').count()
    secretary_count = UserProfile.objects.filter(role='secretary').count()
    pastor_count = UserProfile.objects.filter(role='pastor').count()
    member_count = UserProfile.objects.filter(role='member').count()
    
    for role_code, role_name in UserProfile.ROLE_CHOICES:
        count = UserProfile.objects.filter(role=role_code).count()
        role_stats[role_name] = count
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'recent_logins': recent_logins,
        'role_stats': role_stats,
        'admin_count': admin_count,
        'secretary_count': secretary_count,
        'pastor_count': pastor_count,
        'member_count': member_count,
    }
    return render(request, 'authentication/admin_dashboard.html', context)


@login_required
@user_passes_test(can_manage_users)
def user_management(request):
    """User management interface for admins"""
    search_query = request.GET.get('search', '')
    role_filter = request.GET.get('role', '')
    
    users = User.objects.select_related('profile').all()
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    if role_filter:
        users = users.filter(profile__role=role_filter)
    
    users = users.order_by('-date_joined')
    
    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'role_filter': role_filter,
        'role_choices': UserProfile.ROLE_CHOICES,
    }
    return render(request, 'authentication/user_management.html', context)


@login_required
@user_passes_test(can_manage_users)
def create_user(request):
    """Create new user account"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Log user creation
            log_user_action(
                user=request.user,
                action='manage_user',
                request=request,
                details={'action': 'create_user', 'target_user': user.username}
            )
            
            messages.success(request, f'Mtumiaji {user.username} ameundwa kikamilifu!')
            return redirect('user_management')
    else:
        form = UserRegistrationForm()
    
    context = {'form': form}
    return render(request, 'authentication/create_user.html', context)


@login_required
@user_passes_test(can_manage_users)
@require_http_methods(["POST"])
def toggle_user_status(request, user_id):
    """Toggle user active status (AJAX endpoint)"""
    try:
        user = get_object_or_404(User, id=user_id)
        user.is_active = not user.is_active
        user.save()
        
        # Log action
        log_user_action(
            user=request.user,
            action='manage_user',
            request=request,
            details={
                'action': 'toggle_status',
                'target_user': user.username,
                'new_status': user.is_active
            }
        )
        
        return JsonResponse({
            'success': True,
            'is_active': user.is_active,
            'message': f'Hali ya mtumiaji {user.username} imebadilishwa.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Hitilafu: {str(e)}'
        })


@login_required
@user_passes_test(can_manage_users)
@require_http_methods(["POST"])
def update_user_role(request, user_id):
    """Update user role (AJAX endpoint)"""
    try:
        user = get_object_or_404(User, id=user_id)
        new_role = request.POST.get('role')
        
        if new_role in dict(UserProfile.ROLE_CHOICES):
            # Get or create profile to handle cases where profile doesn't exist
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={'role': 'member'}
            )
            old_role = profile.role
            profile.role = new_role
            profile.save()
            
            # Log action
            log_user_action(
                user=request.user,
                action='manage_user',
                request=request,
                details={
                    'action': 'update_role',
                    'target_user': user.username,
                    'old_role': old_role,
                    'new_role': new_role
                }
            )
            
            return JsonResponse({
                'success': True,
                'new_role': profile.get_role_display(),
                'message': f'Jukumu la mtumiaji {user.username} limebadilishwa.'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Jukumu si halali.'
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Hitilafu: {str(e)}'
        })


@login_required
@user_passes_test(is_admin)
def audit_logs(request):
    """View audit logs for security monitoring"""
    action_filter = request.GET.get('action', '')
    user_filter = request.GET.get('user', '')
    
    logs = AuditLog.objects.select_related('user').all()
    
    if action_filter:
        logs = logs.filter(action=action_filter)
    
    if user_filter:
        logs = logs.filter(user__username__icontains=user_filter)
    
    logs = logs.order_by('-timestamp')
    
    # Pagination
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'action_filter': action_filter,
        'user_filter': user_filter,
        'action_choices': AuditLog.ACTION_CHOICES,
    }
    return render(request, 'authentication/audit_logs.html', context)

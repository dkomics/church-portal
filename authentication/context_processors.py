"""
Context processors for authentication app
"""
from .models import UserProfile


def user_profile_context(request):
    """
    Add user profile information to template context
    """
    context = {}
    
    if request.user.is_authenticated:
        try:
            # Get or create user profile
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            
            # Add profile information to context
            context.update({
                'user_profile': profile,
                'user_role': profile.role,
                'can_register_members': profile.can_register_members(),
                'can_view_directory': profile.can_view_directory(),
                'can_manage_users': profile.can_manage_users(),
                'is_admin': profile.is_admin(),
            })
            
        except Exception as e:
            # Fallback if profile doesn't exist or there's an error
            context.update({
                'user_profile': None,
                'user_role': 'member',
                'can_register_members': False,
                'can_view_directory': False,
                'can_manage_users': False,
                'is_admin': False,
            })
    else:
        # For anonymous users
        context.update({
            'user_profile': None,
            'user_role': None,
            'can_register_members': False,
            'can_view_directory': False,
            'can_manage_users': False,
            'is_admin': False,
        })
    
    return context

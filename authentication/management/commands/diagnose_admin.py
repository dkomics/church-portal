from django.core.management.base import BaseCommand
from django.contrib import admin
from django.contrib.auth.models import User
from django.conf import settings
from authentication.models import UserProfile, AuditLog
from membership.models import Member
import os


class Command(BaseCommand):
    help = 'Diagnose Django admin configuration and data for production troubleshooting'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== DJANGO ADMIN DIAGNOSTICS ==='))
        
        # Check Django settings
        self.stdout.write('\n--- DJANGO SETTINGS ---')
        self.stdout.write(f'DEBUG: {settings.DEBUG}')
        self.stdout.write(f'ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}')
        self.stdout.write(f'DATABASE: {settings.DATABASES["default"]["ENGINE"]}')
        
        # Check installed apps
        self.stdout.write('\n--- INSTALLED APPS ---')
        for app in settings.INSTALLED_APPS:
            self.stdout.write(f'  - {app}')
        
        # Check admin registration
        self.stdout.write('\n--- ADMIN REGISTRATION ---')
        self.stdout.write(f'Total registered models: {len(admin.site._registry)}')
        for model, admin_class in admin.site._registry.items():
            self.stdout.write(f'  - {model._meta.app_label}.{model.__name__}: {admin_class.__class__.__name__}')
        
        # Check database data
        self.stdout.write('\n--- DATABASE DATA ---')
        try:
            user_count = User.objects.count()
            profile_count = UserProfile.objects.count()
            audit_count = AuditLog.objects.count()
            member_count = Member.objects.count()
            
            self.stdout.write(f'Users: {user_count}')
            self.stdout.write(f'UserProfiles: {profile_count}')
            self.stdout.write(f'AuditLogs: {audit_count}')
            self.stdout.write(f'Members: {member_count}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Database error: {e}'))
        
        # Check superusers
        self.stdout.write('\n--- SUPERUSERS ---')
        try:
            superusers = User.objects.filter(is_superuser=True)
            self.stdout.write(f'Superuser count: {superusers.count()}')
            for user in superusers:
                self.stdout.write(f'  - {user.username} (active: {user.is_active}, staff: {user.is_staff})')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Superuser check error: {e}'))
        
        # Check environment variables
        self.stdout.write('\n--- ENVIRONMENT VARIABLES ---')
        env_vars = ['DATABASE_URL', 'DEBUG', 'DJANGO_SECRET_KEY', 'ALLOWED_HOSTS']
        for var in env_vars:
            value = os.getenv(var, 'NOT SET')
            if var == 'DJANGO_SECRET_KEY' and value != 'NOT SET':
                value = f'{value[:10]}...' if len(value) > 10 else value
            self.stdout.write(f'{var}: {value}')
        
        # Check static files
        self.stdout.write('\n--- STATIC FILES ---')
        self.stdout.write(f'STATIC_URL: {settings.STATIC_URL}')
        self.stdout.write(f'STATIC_ROOT: {getattr(settings, "STATIC_ROOT", "NOT SET")}')
        
        self.stdout.write(self.style.SUCCESS('\n=== DIAGNOSTICS COMPLETE ==='))

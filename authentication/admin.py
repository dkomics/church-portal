from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import UserProfile, AuditLog


# Inline UserProfile in User admin
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'
    fields = ('role', 'phone', 'membership_id', 'is_active')
    extra = 0


# Enhanced User Admin with UserProfile inline
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'get_profile_status', 'is_active', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined', 'profile__role')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'profile__phone')
    ordering = ('-date_joined',)
    
    def get_role(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.get_role_display()
        return 'No Profile'
    get_role.short_description = 'Role'
    get_role.admin_order_field = 'profile__role'
    
    def get_profile_status(self, obj):
        if hasattr(obj, 'profile'):
            if obj.profile.is_active:
                return format_html('<span style="color: green;">✓ Active</span>')
            else:
                return format_html('<span style="color: red;">✗ Inactive</span>')
        return format_html('<span style="color: orange;">⚠ No Profile</span>')
    get_profile_status.short_description = 'Profile Status'


# UserProfile Admin
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'membership_id', 'is_active', 'created_at')
    list_display_links = ('user',)
    list_filter = ('role', 'is_active', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'phone', 'membership_id')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Profile Details', {
            'fields': ('role', 'phone', 'membership_id')
        }),
        ('Status & Timestamps', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


# AuditLog Admin
@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'target_member_id', 'ip_address', 'get_details_summary')
    list_display_links = ('timestamp',)
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'target_member_id', 'ip_address')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)
    
    fieldsets = (
        ('Action Information', {
            'fields': ('user', 'action', 'target_member_id')
        }),
        ('Request Details', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('timestamp', 'details'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('timestamp',)
    
    def get_details_summary(self, obj):
        if obj.details:
            # Show first 50 characters of details
            details_str = str(obj.details)[:50]
            if len(str(obj.details)) > 50:
                details_str += '...'
            return details_str
        return '-'
    get_details_summary.short_description = 'Details Summary'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    def has_add_permission(self, request):
        # Audit logs should not be manually created
        return False
    
    def has_change_permission(self, request, obj=None):
        # Audit logs should not be modified
        return False


# Re-register User admin with our enhanced version
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Customize admin site headers
admin.site.site_header = 'Church Portal Administration'
admin.site.site_title = 'Church Portal Admin'
admin.site.index_title = 'Welcome to Church Portal Administration'

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Member, Branch, AttendanceSession, AttendanceRecord, News, NewsCategory

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    # Simplified display configuration
    list_display = ['membership_id', 'full_name', 'branch', 'gender', 'phone', 'registration_date']
    list_display_links = ['membership_id', 'full_name']
    
    # Basic filtering
    list_filter = ['branch', 'gender', 'age_category', 'membership_type', 'baptized']
    
    # Search functionality
    search_fields = ['full_name', 'membership_id', 'phone', 'email']
    
    # Ordering
    ordering = ['-registration_date', 'full_name']
    
    # Simplified fieldsets
    fieldsets = (
        ('Basic Information', {
            'fields': ('membership_id', 'branch', 'full_name', 'gender', 'age_category')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email', 'address'),
        }),
        ('Spiritual Information', {
            'fields': ('baptized', 'baptism_date', 'membership_class'),
        }),
        ('Membership Details', {
            'fields': ('membership_type', 'registration_date')
        })
    )
    
    # Read-only fields
    readonly_fields = ['membership_id']
    
    # Items per page
    list_per_page = 25


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'pastor_name', 'get_member_count', 'established_date', 'is_active']
    list_filter = ['is_active', 'established_date']
    search_fields = ['name', 'code', 'pastor_name', 'address']
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'pastor_name', 'established_date', 'is_active')
        }),
        ('Contact Information', {
            'fields': ('address', 'phone', 'email'),
            'classes': ('collapse',)
        }),
    )
    
    def get_member_count(self, obj):
        return obj.get_member_count()
    get_member_count.short_description = 'Members'


@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    ordering = ['name']


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'scope', 'branch', 'category', 'priority', 'author', 'publish_date', 'is_published']
    list_filter = ['scope', 'branch', 'category', 'priority', 'is_published', 'publish_date']
    search_fields = ['title', 'content', 'author__username']
    date_hierarchy = 'publish_date'
    ordering = ['-publish_date']
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'content', 'category')
        }),
        ('Publishing', {
            'fields': ('scope', 'branch', 'priority', 'publish_date', 'expiry_date', 'is_published', 'is_featured')
        }),
        ('Metadata', {
            'fields': ('author',),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ['title', 'branch', 'service_type', 'date', 'start_time', 'get_attendance_count', 'created_by']
    list_filter = ['branch', 'service_type', 'date', 'is_active']
    search_fields = ['title', 'description']
    date_hierarchy = 'date'
    ordering = ['-date', '-start_time']
    
    fieldsets = (
        ('Session Details', {
            'fields': ('title', 'branch', 'service_type', 'description')
        }),
        ('Schedule', {
            'fields': ('date', 'start_time', 'end_time', 'is_active')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['member', 'session', 'marked_by', 'marked_at']
    list_filter = ['session__branch', 'session__service_type', 'session__date', 'marked_at']
    search_fields = ['member__full_name', 'session__title', 'notes']
    date_hierarchy = 'marked_at'
    ordering = ['-marked_at']
    
    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.marked_by = request.user
        super().save_model(request, obj, form, change)

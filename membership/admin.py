from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Member

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    # Display configuration
    list_display = [
        'membership_id', 'get_display_name', 'gender', 'age_category', 
        'get_contact_info', 'membership_type', 'is_baptized', 
        'registration_date', 'get_member_actions'
    ]
    
    list_display_links = ['membership_id', 'get_display_name']
    
    # Filtering options
    list_filter = [
        'gender', 'age_category', 'membership_type', 'baptized', 
        'membership_class', 'marital_status', 'registration_date'
    ]
    
    # Search functionality
    search_fields = [
        'full_name', 'membership_id', 'phone', 'email', 
        'emergency_phone', 'address', 'emergency_name'
    ]
    
    # Date hierarchy
    date_hierarchy = 'registration_date'
    
    # Ordering
    ordering = ['-registration_date', 'full_name']
    
    # Fields organization
    fieldsets = (
        ('Taarifa za Kimsingi', {
            'fields': ('membership_id', 'full_name', 'gender', 'age_category')
        }),
        ('Taarifa za Kibinafsi', {
            'fields': ('dob', 'marital_status', 'address'),
            'classes': ('collapse',)
        }),
        ('Taarifa za Mawasiliano', {
            'fields': ('phone', 'email'),
            'classes': ('collapse',)
        }),
        ('Taarifa za Kiroho', {
            'fields': ('salvation_date', 'baptized', 'baptism_date', 'membership_class', 'previous_church'),
            'classes': ('collapse',)
        }),
        ('Mtu wa Dharura', {
            'fields': ('emergency_name', 'emergency_relation', 'emergency_phone'),
            'classes': ('collapse',)
        }),
        ('Taarifa za Ushirika', {
            'fields': ('membership_type', 'registration_date')
        })
    )
    
    # Read-only fields
    readonly_fields = ['membership_id']
    
    # Items per page
    list_per_page = 25
    
    # Custom methods for display
    def get_display_name(self, obj):
        """Display formatted name with title case"""
        return obj.get_display_name()
    get_display_name.short_description = 'Jina Kamili'
    get_display_name.admin_order_field = 'full_name'
    
    def get_contact_info(self, obj):
        """Display contact information"""
        contacts = []
        if obj.phone:
            contacts.append(f"📱 {obj.phone}")
        if obj.email:
            contacts.append(f"📧 {obj.email}")
        return ' | '.join(contacts) if contacts else '❌ Hakuna'
    get_contact_info.short_description = 'Mawasiliano'
    
    def is_baptized(self, obj):
        """Display baptism status with icons"""
        if obj.baptized == 'Yes':
            return format_html('<span style="color: green;">✅ Ndio</span>')
        else:
            return format_html('<span style="color: red;">❌ Hapana</span>')
    is_baptized.short_description = 'Amebatizwa'
    is_baptized.admin_order_field = 'baptized'
    
    def get_member_actions(self, obj):
        """Display action buttons"""
        return format_html(
            '<a class="button" href="{}">👁️ Ona</a>',
            reverse('admin:membership_member_change', args=[obj.pk])
        )
    get_member_actions.short_description = 'Vitendo'
    
    # Custom actions
    def mark_as_baptized(self, request, queryset):
        """Mark selected members as baptized"""
        updated = queryset.update(baptized='Yes', baptism_date=timezone.now().date())
        self.message_user(request, f'{updated} washirika wamewekwa alama ya kubatizwa.')
    mark_as_baptized.short_description = 'Weka alama ya kubatizwa'
    
    def mark_membership_class_complete(self, request, queryset):
        """Mark membership class as completed"""
        updated = queryset.update(membership_class='Yes')
        self.message_user(request, f'{updated} washirika wamekamilisha darasa la ushirika.')
    mark_membership_class_complete.short_description = 'Kamilisha darasa la ushirika'
    
    def export_member_list(self, request, queryset):
        """Export selected members to CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="washirika.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID Ushirika', 'Jina Kamili', 'Jinsia', 'Umri', 'Simu', 'Email', 
            'Anuani', 'Amebatizwa', 'Aina ya Ushirika', 'Tarehe ya Usajili'
        ])
        
        for member in queryset:
            writer.writerow([
                member.membership_id, member.full_name, member.get_gender_display(),
                member.age_category, member.phone, member.email, member.address,
                member.get_baptized_display(), member.get_membership_type_display(),
                member.registration_date
            ])
        
        return response
    export_member_list.short_description = 'Hamisha orodha ya washirika (CSV)'
    
    actions = ['mark_as_baptized', 'mark_membership_class_complete', 'export_member_list']
    
    # Custom CSS and JS
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('admin/js/custom_admin.js',)
    
    def get_queryset(self, request):
        """Optimize queryset for admin list view"""
        return super().get_queryset(request).select_related()
    
    def save_model(self, request, obj, form, change):
        """Custom save logic"""
        if not change:  # New object
            # Log new member creation
            from django.contrib.admin.models import LogEntry, ADDITION
            from django.contrib.contenttypes.models import ContentType
            
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(obj).pk,
                object_id=obj.pk,
                object_repr=str(obj),
                action_flag=ADDITION,
                change_message=f'Mshirika mpya amesajiliwa: {obj.full_name}'
            )
        
        super().save_model(request, obj, form, change)

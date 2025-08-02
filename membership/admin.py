from django.contrib import admin
from .models import Member
@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'email', 'membership_type', 'registration_date']
    search_fields = ['full_name', 'phone', 'email']

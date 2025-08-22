from django.contrib.auth.models import User, Group
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """Extended user profile for church members with roles and permissions"""
    
    ROLE_CHOICES = [
        ('member', 'Member'),
        ('secretary', 'Secretary/Clerk'),
        ('pastor', 'Pastor/Leader'),
        ('branch_admin', 'Branch Administrator'),
        ('admin', 'System Administrator'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    
    # Branch assignment - users can only access their assigned branches
    branches = models.ManyToManyField('membership.Branch', blank=True, related_name='users',
                                    help_text="Branches this user has access to")
    primary_branch = models.ForeignKey('membership.Branch', on_delete=models.SET_NULL, 
                                     null=True, blank=True, related_name='primary_users',
                                     help_text="Primary branch for this user")
    
    phone = models.CharField(max_length=15, blank=True, null=True)
    membership_id = models.CharField(max_length=20, blank=True, null=True, 
                                   help_text="Link to member record if applicable")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'auth_user_profile'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"
    
    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username
    
    @property
    def can_register_members(self):
        """Check if user can register new members"""
        return self.role in ['secretary', 'pastor', 'branch_admin', 'admin']
    
    @property
    def can_view_directory(self):
        """Check if user can view member directory"""
        return self.role in ['secretary', 'pastor', 'branch_admin', 'admin']
    
    @property
    def can_view_full_details(self):
        """Check if user can view full member details"""
        return self.role in ['pastor', 'branch_admin', 'admin']
    
    @property
    def can_manage_users(self):
        """Check if user can manage other users"""
        return self.role in ['branch_admin', 'admin']
    
    @property
    def can_export_data(self):
        """Check if user can export member data"""
        return self.role in ['secretary', 'pastor', 'branch_admin', 'admin']
    
    @property
    def can_manage_attendance(self):
        """Check if user can manage attendance"""
        return self.role in ['secretary', 'pastor', 'branch_admin', 'admin']
    
    @property
    def can_manage_news(self):
        """Check if user can create/edit news"""
        return self.role in ['pastor', 'branch_admin', 'admin']
    
    @property
    def is_system_admin(self):
        """Check if user is system administrator (can access all branches)"""
        return self.role == 'admin'
    
    @property
    def is_branch_admin(self):
        """Check if user is branch administrator"""
        return self.role == 'branch_admin'
    
    def get_accessible_branches(self):
        """Get branches this user can access"""
        if self.is_system_admin:
            from membership.models import Branch
            return Branch.objects.filter(is_active=True)
        return self.branches.filter(is_active=True)
    
    def can_access_branch(self, branch):
        """Check if user can access a specific branch"""
        if self.is_system_admin:
            return True
        return self.branches.filter(id=branch.id).exists()
    
    def get_accessible_members(self):
        """Get members this user can access"""
        from membership.models import Member
        if self.is_system_admin:
            return Member.objects.all()
        accessible_branches = self.get_accessible_branches()
        return Member.objects.filter(branch__in=accessible_branches)
    
    def get_accessible_member_fields(self):
        """Return list of member fields this user can access"""
        if self.role == 'admin' or self.role == 'pastor':
            return 'all'  # Full access
        elif self.role == 'secretary':
            return ['full_name', 'gender', 'phone', 'email', 'address', 
                   'membership_type', 'registration_date', 'membership_id']
        else:
            return ['full_name', 'membership_type']  # Limited access


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create UserProfile when User is created"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when User is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()


class AuditLog(models.Model):
    """Track user actions for security and compliance"""
    
    ACTION_CHOICES = [
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('view_member', 'View Member Details'),
        ('register_member', 'Register New Member'),
        ('update_member', 'Update Member Information'),
        ('export_data', 'Export Member Data'),
        ('manage_user', 'User Management Action'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    target_member_id = models.CharField(max_length=20, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(blank=True, null=True, help_text="Additional action details")
    
    class Meta:
        db_table = 'auth_audit_log'
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()} at {self.timestamp}"

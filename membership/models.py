from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from django.contrib.auth.models import User
import uuid


class Branch(models.Model):
    """Model for different church branches/locations"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True, help_text="Short code for the branch (e.g., 'ARU', 'DAR')")
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    pastor_name = models.CharField(max_length=100, blank=True)
    established_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Tawi"
        verbose_name_plural = "Matawi"
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def get_member_count(self):
        """Get total number of active members in this branch"""
        return self.members.count()
    
    def get_recent_members(self, days=30):
        """Get members registered in the last N days"""
        from django.utils import timezone
        cutoff_date = timezone.now().date() - timezone.timedelta(days=days)
        return self.members.filter(registration_date__gte=cutoff_date)


class Member(models.Model):
    GENDER_CHOICES = [('Male', 'Mwanaume'), ('Female', 'Mwanamke'), ('Prefer not to say', 'Sipendi kusema')]
    MARITAL_CHOICES = [('Single', 'Bila ndoa'), ('Married', 'Kwenye ndoa'), ('Divorced', 'Talaka'), ('Widowed', 'Mjane')]
    BAPTIZED_CHOICES = [('Yes', 'Ndio'), ('No', 'Hapana')]
    CLASS_CHOICES = [('Yes', 'Ndio'), ('No', 'Hapana'), ('Not Yet', 'Bado')]
    MEMBERSHIP_CHOICES = [('New', 'Mshirika Mpya'), ('Transfer', 'Aliyehamia'), ('Returning', 'Anayerudi')]

    # Branch relationship - REQUIRED field
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='members', null=True, blank=True)
    
    full_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    age_category = models.CharField(
        max_length=20,
        choices=[('Mtoto','Mtoto'),('Kijana','Kijana'),('Mtu mzima','Mtu mzima')],
        default='Mtu mzima'
    )

    dob = models.DateField(null=True, blank=True)
    marital_status = models.CharField(max_length=20, choices=MARITAL_CHOICES, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=255)

    salvation_date = models.DateField(null=True, blank=True)
    baptized = models.CharField(max_length=5, choices=BAPTIZED_CHOICES)
    baptism_date = models.DateField(null=True, blank=True)

    membership_class = models.CharField(max_length=10, choices=CLASS_CHOICES, blank=True)
    previous_church = models.CharField(max_length=100, blank=True)

    emergency_name = models.CharField(max_length=100)
    emergency_relation = models.CharField(max_length=50)
    emergency_phone = models.CharField(max_length=15)

    membership_type = models.CharField(max_length=20, choices=MEMBERSHIP_CHOICES)
    registration_date = models.DateField()
    membership_id = models.CharField(
        max_length=8,
        unique=True,
        blank=True,    # allows it to be empty at creation
        null=True,     # stores NULL in the DB until set
        editable=True  # admin can edit it in the Django admin UI
    )
    def save(self, *args, **kwargs):
        # Skip auto-generation in admin to prevent errors
        super().save(*args, **kwargs)
    
    def generate_membership_id(self):
        """Generate a unique membership ID with branch code"""
        # Check if branch is assigned
        if not self.branch:
            # Return a temporary ID or use default branch
            year = timezone.now().year
            return f"TEMP{year}{timezone.now().microsecond:06d}"
        
        # Format: BRANCH_CODE + YEAR + 4-digit sequential number
        year = timezone.now().year
        branch_code = self.branch.code.upper()
        prefix = f"{branch_code}{year}"
        
        last_member = Member.objects.filter(
            branch=self.branch,
            membership_id__startswith=prefix
        ).order_by('membership_id').last()
        
        if last_member and last_member.membership_id:
            try:
                last_number = int(last_member.membership_id[len(prefix):])
                new_number = last_number + 1
            except (ValueError, IndexError):
                new_number = 1
        else:
            new_number = 1
        
        return f"{prefix}{new_number:04d}"
    
    @property
    def age_from_dob(self):
        """Calculate age from date of birth"""
        if self.dob:
            today = timezone.now().date()
            return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
        return None
    
    @property
    def is_baptized(self):
        """Check if member is baptized"""
        return self.baptized == 'Yes'
    
    @property
    def has_completed_membership_class(self):
        """Check if member has completed membership class"""
        return self.membership_class == 'Yes'
    
    def get_display_name(self):
        """Get formatted display name"""
        return self.full_name.title()
    
    def get_contact_info(self):
        """Get formatted contact information"""
        contacts = []
        if self.phone:
            contacts.append(f"Simu: {self.phone}")
        if self.email:
            contacts.append(f"Email: {self.email}")
        return " | ".join(contacts) if contacts else "Hakuna taarifa za mawasiliano"
    
    class Meta:
        ordering = ['-registration_date', 'full_name']
        verbose_name = "Mshirika"
        verbose_name_plural = "Washirika"
        indexes = [
            models.Index(fields=['membership_id']),
            models.Index(fields=['full_name']),
            models.Index(fields=['registration_date']),
            models.Index(fields=['membership_type']),
        ]
    
    def __str__(self):
        return f"{self.membership_id} - {self.full_name}" if self.membership_id else self.full_name


class AttendanceSession(models.Model):
    """Model for tracking attendance sessions (services, events, etc.)"""
    SERVICE_TYPES = [
        ('sunday_service', 'Sunday Service'),
        ('prayer_meeting', 'Prayer Meeting'),
        ('bible_study', 'Bible Study'),
        ('youth_service', 'Youth Service'),
        ('special_event', 'Special Event'),
        ('other', 'Other'),
    ]
    
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='attendance_sessions')
    title = models.CharField(max_length=200)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_sessions')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-date', '-start_time']
        verbose_name = "Kipindi cha Mahudhurio"
        verbose_name_plural = "Vipindi vya Mahudhurio"
        unique_together = ['branch', 'date', 'start_time', 'service_type']
    
    def __str__(self):
        return f"{self.title} - {self.branch.name} ({self.date})"
    
    def get_attendance_count(self):
        """Get total attendance for this session"""
        return self.attendance_records.count()
    
    def get_attendance_percentage(self):
        """Calculate attendance percentage based on branch membership"""
        total_members = self.branch.get_member_count()
        if total_members == 0:
            return 0
        return round((self.get_attendance_count() / total_members) * 100, 2)


class AttendanceRecord(models.Model):
    """Model for individual attendance records"""
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name='attendance_records')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='attendance_records')
    marked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='marked_attendance')
    marked_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['session', 'member']
        verbose_name = "Rekodi ya Mahudhurio"
        verbose_name_plural = "Rekodi za Mahudhurio"
        ordering = ['-marked_at']
    
    def __str__(self):
        return f"{self.member.full_name} - {self.session.title}"


class NewsCategory(models.Model):
    """Categories for news and announcements"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#007bff', help_text="Hex color code for category")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Jamii ya Habari"
        verbose_name_plural = "Jamii za Habari"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class News(models.Model):
    """Model for news and announcements"""
    SCOPE_CHOICES = [
        ('general', 'General Church News'),
        ('branch', 'Branch Specific'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    scope = models.CharField(max_length=10, choices=SCOPE_CHOICES)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='news', 
                              null=True, blank=True, help_text="Required for branch-specific news")
    category = models.ForeignKey(NewsCategory, on_delete=models.SET_NULL, null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_news')
    publish_date = models.DateTimeField()
    expiry_date = models.DateTimeField(null=True, blank=True, help_text="Optional expiry date")
    
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-publish_date', '-priority']
        verbose_name = "Habari"
        verbose_name_plural = "Habari"
        indexes = [
            models.Index(fields=['scope', 'branch']),
            models.Index(fields=['publish_date', 'is_published']),
            models.Index(fields=['priority', 'is_featured']),
        ]
    
    def __str__(self):
        scope_display = f"({self.branch.name})" if self.scope == 'branch' and self.branch else "(General)"
        return f"{self.title} {scope_display}"
    
    def is_active(self):
        """Check if news is currently active"""
        now = timezone.now()
        if not self.is_published:
            return False
        if self.publish_date > now:
            return False
        if self.expiry_date and self.expiry_date < now:
            return False
        return True
    
    def clean(self):
        """Validate that branch-specific news has a branch assigned"""
        from django.core.exceptions import ValidationError
        if self.scope == 'branch' and not self.branch:
            raise ValidationError("Branch-specific news must have a branch assigned.")
        if self.scope == 'general' and self.branch:
            raise ValidationError("General news should not have a branch assigned.")

from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
import uuid

class Member(models.Model):
    GENDER_CHOICES = [('Male', 'Mwanaume'), ('Female', 'Mwanamke'), ('Prefer not to say', 'Sipendi kusema')]
    MARITAL_CHOICES = [('Single', 'Bila ndoa'), ('Married', 'Kwenye ndoa'), ('Divorced', 'Talaka'), ('Widowed', 'Mjane')]
    BAPTIZED_CHOICES = [('Yes', 'Ndio'), ('No', 'Hapana')]
    CLASS_CHOICES = [('Yes', 'Ndio'), ('No', 'Hapana'), ('Not Yet', 'Bado')]
    MEMBERSHIP_CHOICES = [('New', 'Mshirika Mpya'), ('Transfer', 'Aliyehamia'), ('Returning', 'Anayerudi')]

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
        # Auto-generate membership ID if not provided
        if not self.membership_id:
            self.membership_id = self.generate_membership_id()
        super().save(*args, **kwargs)
    
    def generate_membership_id(self):
        """Generate a unique membership ID"""
        # Format: YEAR + 4-digit sequential number
        year = timezone.now().year
        last_member = Member.objects.filter(
            membership_id__startswith=str(year)
        ).order_by('membership_id').last()
        
        if last_member and last_member.membership_id:
            try:
                last_number = int(last_member.membership_id[4:])
                new_number = last_number + 1
            except (ValueError, IndexError):
                new_number = 1
        else:
            new_number = 1
        
        return f"{year}{new_number:04d}"
    
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

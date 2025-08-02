from django.db import models

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
    def __str__(self):
        return self.full_name

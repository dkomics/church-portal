# membership/serializers.py

from rest_framework import serializers
from .models import Member

class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = [
            'full_name', 'gender', 'age_category', 'dob', 'marital_status',
            'phone', 'email', 'address', 'salvation_date', 'baptized',
            'baptism_date', 'membership_class', 'previous_church',
            'emergency_name', 'emergency_relation', 'emergency_phone',
            'membership_type', 'registration_date'
        ]
        extra_kwargs = {
            # required=True is default for all, so we explicitly set false for optional
            'dob':             {'required': False, 'allow_null': True},
            'marital_status':  {'required': False, 'allow_blank': True},
            'phone':           {'required': False, 'allow_blank': True},
            'email':           {'required': False, 'allow_blank': True},
            'salvation_date':  {'required': False, 'allow_null': True},
            'baptism_date':    {'required': False, 'allow_null': True},
            'membership_class':{'required': False, 'allow_blank': True},
            'previous_church': {'required': False, 'allow_blank': True},
        }

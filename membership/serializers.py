# membership/serializers.py

from rest_framework import serializers
from django.utils import timezone
from datetime import date
import re
from .models import Member

class MemberSerializer(serializers.ModelSerializer):
    # Add computed fields for better API responses
    age_from_dob = serializers.ReadOnlyField()
    is_baptized = serializers.ReadOnlyField()
    has_completed_membership_class = serializers.ReadOnlyField()
    display_name = serializers.SerializerMethodField()
    contact_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Member
        fields = [
            'membership_id', 'full_name', 'display_name', 'gender', 'age_category', 
            'dob', 'age_from_dob', 'marital_status', 'phone', 'email', 'address', 
            'contact_info', 'salvation_date', 'baptized', 'is_baptized',
            'baptism_date', 'membership_class', 'has_completed_membership_class', 
            'previous_church', 'emergency_name', 'emergency_relation', 'emergency_phone',
            'membership_type', 'registration_date'
        ]
        read_only_fields = ['membership_id', 'age_from_dob', 'is_baptized', 
                           'has_completed_membership_class', 'display_name', 'contact_info']
        extra_kwargs = {
            # Optional fields
            'dob':             {'required': False, 'allow_null': True},
            'marital_status':  {'required': False, 'allow_blank': True},
            'phone':           {'required': False, 'allow_blank': True},
            'email':           {'required': False, 'allow_blank': True},
            'salvation_date':  {'required': False, 'allow_null': True},
            'baptism_date':    {'required': False, 'allow_null': True},
            'membership_class':{'required': False, 'allow_blank': True},
            'previous_church': {'required': False, 'allow_blank': True},
            # Better error messages
            'full_name': {'error_messages': {'required': 'Jina kamili ni lazima.', 'blank': 'Jina kamili haliwezi kuwa tupu.'}},
            'gender': {'error_messages': {'required': 'Jinsia ni lazima.', 'invalid_choice': 'Chagua jinsia sahihi.'}},
            'age_category': {'error_messages': {'required': 'Kundi la umri ni lazima.', 'invalid_choice': 'Chagua kundi sahihi la umri.'}},
            'address': {'error_messages': {'required': 'Anuani ni lazima.', 'blank': 'Anuani haiwezi kuwa tupu.'}},
            'baptized': {'error_messages': {'required': 'Taarifa ya ubatizo ni lazima.', 'invalid_choice': 'Chagua jibu sahihi la ubatizo.'}},
            'emergency_name': {'error_messages': {'required': 'Jina la mtu wa dharura ni lazima.', 'blank': 'Jina la mtu wa dharura haliwezi kuwa tupu.'}},
            'emergency_relation': {'error_messages': {'required': 'Mahusiano ya mtu wa dharura ni lazima.', 'blank': 'Mahusiano haiwezi kuwa tupu.'}},
            'emergency_phone': {'error_messages': {'required': 'Namba ya simu ya dharura ni lazima.', 'blank': 'Namba ya simu haiwezi kuwa tupu.'}},
            'membership_type': {'error_messages': {'required': 'Aina ya ushirika ni lazima.', 'invalid_choice': 'Chagua aina sahihi ya ushirika.'}},
            'registration_date': {'error_messages': {'required': 'Tarehe ya usajili ni lazima.', 'invalid': 'Ingiza tarehe sahihi.'}},
        }
    
    def get_display_name(self, obj):
        """Get formatted display name"""
        return obj.get_display_name()
    
    def get_contact_info(self, obj):
        """Get formatted contact information"""
        return obj.get_contact_info()
    
    def validate_phone(self, value):
        """Validate phone number format (Kenyan format)"""
        if value:
            # Remove spaces and common separators
            phone = re.sub(r'[\s\-\(\)]', '', value)
            # Check Kenyan phone number format
            if not re.match(r'^(\+254|0)[17]\d{8}$', phone):
                raise serializers.ValidationError(
                    'Namba ya simu si sahihi. Tumia mfumo wa Kenya (mfano: 0712345678 au +254712345678).'
                )
        return value
    
    def validate_emergency_phone(self, value):
        """Validate emergency phone number format"""
        if value:
            phone = re.sub(r'[\s\-\(\)]', '', value)
            if not re.match(r'^(\+254|0)[17]\d{8}$', phone):
                raise serializers.ValidationError(
                    'Namba ya simu ya dharura si sahihi. Tumia mfumo wa Kenya (mfano: 0712345678).'
                )
        return value
    
    def validate_email(self, value):
        """Validate email format"""
        if value:
            # Basic email validation (Django handles most of this)
            if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', value):
                raise serializers.ValidationError('Barua pepe si sahihi.')
        return value
    
    def validate_dob(self, value):
        """Validate date of birth"""
        if value:
            today = date.today()
            if value > today:
                raise serializers.ValidationError('Tarehe ya kuzaliwa haiwezi kuwa baadaye.')
            # Check if age is reasonable (not older than 150 years)
            age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
            if age > 150:
                raise serializers.ValidationError('Tarehe ya kuzaliwa si ya kawaida.')
        return value
    
    def validate_registration_date(self, value):
        """Validate registration date"""
        if value:
            today = date.today()
            if value > today:
                raise serializers.ValidationError('Tarehe ya usajili haiwezi kuwa baadaye.')
            # Allow registration dates up to 2 years in the past
            if (today - value).days > 730:
                raise serializers.ValidationError('Tarehe ya usajili ni ya zamani sana.')
        return value
    
    def validate_salvation_date(self, value):
        """Validate salvation date"""
        if value:
            today = date.today()
            if value > today:
                raise serializers.ValidationError('Tarehe ya kuokoka haiwezi kuwa baadaye.')
        return value
    
    def validate_baptism_date(self, value):
        """Validate baptism date"""
        if value:
            today = date.today()
            if value > today:
                raise serializers.ValidationError('Tarehe ya ubatizo haiwezi kuwa baadaye.')
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        errors = {}
        
        # If baptized is 'Yes', baptism_date should be provided (optional but recommended)
        if data.get('baptized') == 'Yes' and not data.get('baptism_date'):
            # This is just a warning, not an error
            pass
        
        # If baptized is 'No', baptism_date should not be provided
        if data.get('baptized') == 'No' and data.get('baptism_date'):
            errors['baptism_date'] = 'Tarehe ya ubatizo haiwezi kuwepo kama hajabatizwa.'
        
        # Validate that salvation_date is before baptism_date if both are provided
        salvation_date = data.get('salvation_date')
        baptism_date = data.get('baptism_date')
        if salvation_date and baptism_date and salvation_date > baptism_date:
            errors['baptism_date'] = 'Tarehe ya ubatizo haiwezi kuwa kabla ya tarehe ya kuokoka.'
        
        # Validate that dob is before salvation_date if both are provided
        dob = data.get('dob')
        if dob and salvation_date and dob > salvation_date:
            errors['salvation_date'] = 'Tarehe ya kuokoka haiwezi kuwa kabla ya tarehe ya kuzaliwa.'
        
        # Validate age category matches actual age if dob is provided
        if dob:
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            age_category = data.get('age_category')
            
            if age_category == 'Mtoto' and age >= 13:
                errors['age_category'] = 'Umri haulingani na kundi la umri lililochaguliwa.'
            elif age_category == 'Kijana' and (age < 13 or age > 25):
                errors['age_category'] = 'Umri haulingani na kundi la umri lililochaguliwa.'
            elif age_category == 'Mtu mzima' and age < 25:
                errors['age_category'] = 'Umri haulingani na kundi la umri lililochaguliwa.'
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data

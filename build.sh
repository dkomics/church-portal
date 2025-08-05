#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Handle migration conflicts with comprehensive database state check
echo "Running database migrations with comprehensive conflict resolution..."

# Create a custom migration script to handle the specific conflicts
python manage.py shell << 'MIGRATION_EOF'
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_portal.settings')

import django
django.setup()

from django.db import connection
from django.core.management import call_command
from django.db.utils import ProgrammingError

print("Checking database state...")

# Check what columns actually exist
with connection.cursor() as cursor:
    try:
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'membership_member'
            AND column_name IN ('age_category', 'membership_id');
        """)
        existing_columns = [row[0] for row in cursor.fetchall()]
        print(f"Existing columns: {existing_columns}")
        
        has_age_category = 'age_category' in existing_columns
        has_membership_id = 'membership_id' in existing_columns
        
        print(f"Has age_category: {has_age_category}")
        print(f"Has membership_id: {has_membership_id}")
        
        if has_age_category and not has_membership_id:
            print("Detected partial migration 0002 - age_category exists but membership_id missing")
            print("Adding missing membership_id column...")
            cursor.execute("""
                ALTER TABLE membership_member 
                ADD COLUMN membership_id VARCHAR(8) NULL UNIQUE;
            """)
            print("membership_id column added successfully")
            
        elif has_age_category and has_membership_id:
            print("Both columns exist - marking migration 0002 as fake")
            call_command('migrate', 'membership', '0002', '--fake')
            
        elif not has_age_category and not has_membership_id:
            print("No columns exist - running normal migration")
            
    except Exception as e:
        print(f"Error checking database state: {e}")
        print("Proceeding with fallback migration strategy...")

print("Database state check completed")
MIGRATION_EOF

# Now run migrations normally
echo "Running migrations after state resolution..."
python manage.py migrate

# Create superuser if it doesn't exist (for production)
python manage.py shell << EOF
from django.contrib.auth.models import User
from authentication.models import UserProfile

# Create superuser if it doesn't exist
if not User.objects.filter(username='admin').exists():
    user = User.objects.create_superuser(
        username='admin',
        email='admin@church.com',
        password='ChurchAdmin2024!'
    )
    print(f"Superuser created: {user.username}")
else:
    print("Superuser already exists")

# Ensure UserProfile exists for admin
admin_user = User.objects.get(username='admin')
if not hasattr(admin_user, 'profile'):
    profile = UserProfile.objects.create(
        user=admin_user,
        role='admin',
        phone_number='+255000000000'
    )
    print(f"Admin profile created: {profile}")
else:
    print("Admin profile already exists")
EOF

echo "Build completed successfully!"

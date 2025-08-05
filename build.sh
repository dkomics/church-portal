#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run database migrations with conflict resolution
echo "Running database migrations safely..."
python manage.py safe_migrate

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

#!/usr/bin/env python
"""
Check static files configuration and collection status
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_portal.settings')
django.setup()

from django.conf import settings
from django.contrib.staticfiles.finders import find
from django.core.management import execute_from_command_line

def check_static_files():
    """Check static files configuration and collection"""
    print("=== STATIC FILES DIAGNOSTIC ===")
    
    print(f"STATIC_URL: {settings.STATIC_URL}")
    print(f"STATIC_ROOT: {getattr(settings, 'STATIC_ROOT', 'Not configured')}")
    print(f"STATICFILES_DIRS: {getattr(settings, 'STATICFILES_DIRS', [])}")
    
    # Check critical static files
    critical_files = [
        'css/home.css',
        'css/admin_dashboard.css', 
        'css/directory.css',
        'js/home.js',
        'js/admin_dashboard.js',
        'js/directory.js',
        'images/background.jpg'
    ]
    
    print(f"\nChecking {len(critical_files)} critical static files:")
    missing_files = []
    
    for file_path in critical_files:
        found = find(file_path)
        if found:
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - NOT FOUND")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  {len(missing_files)} files missing - this could cause 500 errors")
        print("Run: python manage.py collectstatic --noinput")
    else:
        print("\n✅ All critical static files found")
    
    # Check if STATIC_ROOT directory exists and has files
    static_root = getattr(settings, 'STATIC_ROOT', None)
    if static_root:
        static_path = Path(static_root)
        if static_path.exists():
            file_count = len(list(static_path.rglob('*')))
            print(f"\nSTATIC_ROOT directory: ✅ {file_count} files")
        else:
            print(f"\nSTATIC_ROOT directory: ❌ Does not exist")
            print("Run: python manage.py collectstatic --noinput")
    
    return len(missing_files) == 0

if __name__ == "__main__":
    check_static_files()

#!/usr/bin/env python
"""
Production debugging script to identify Server Error (500) causes
Run this on production server to get detailed error information
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

from django.test import RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.sessions.backends.db import SessionStore
from membership.views import home_page
from authentication.context_processors import user_profile_context
import traceback

def debug_production_500():
    """Comprehensive debugging for production 500 errors"""
    print("=== PRODUCTION 500 ERROR DEBUGGING ===")
    print(f"Django version: {django.get_version()}")
    print(f"Python version: {sys.version}")
    
    # Check environment
    print(f"\nEnvironment:")
    print(f"DEBUG: {os.getenv('DEBUG', 'Not set')}")
    print(f"DATABASE_URL: {'Set' if os.getenv('DATABASE_URL') else 'Not set'}")
    
    factory = RequestFactory()
    
    try:
        # Test 1: Anonymous user
        print("\n1. Testing Anonymous User...")
        request = factory.get('/')
        request.session = SessionStore()
        request.user = AnonymousUser()
        
        # Test context processor first
        context = user_profile_context(request)
        print(f"   Context processor: ✅ {len(context)} variables")
        
        # Test view
        response = home_page(request)
        print(f"   Home page view: ✅ Status {response.status_code}")
        
    except Exception as e:
        print(f"   ❌ Anonymous user error: {e}")
        print(f"   Error type: {type(e).__name__}")
        traceback.print_exc()
        return False
    
    try:
        # Test 2: Authenticated user
        print("\n2. Testing Authenticated User...")
        users = User.objects.all()[:1]
        if users:
            request.user = users[0]
            response = home_page(request)
            print(f"   Authenticated view: ✅ Status {response.status_code}")
        else:
            print("   No users found in database")
            
    except Exception as e:
        print(f"   ❌ Authenticated user error: {e}")
        print(f"   Error type: {type(e).__name__}")
        traceback.print_exc()
        return False
    
    try:
        # Test 3: Database queries
        print("\n3. Testing Database Queries...")
        from membership.models import Member, Branch, News
        from authentication.models import UserProfile
        
        print(f"   Members: {Member.objects.count()}")
        print(f"   Branches: {Branch.objects.count()}")
        print(f"   News: {News.objects.count()}")
        print(f"   UserProfiles: {UserProfile.objects.count()}")
        print("   Database queries: ✅")
        
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        traceback.print_exc()
        return False
    
    try:
        # Test 4: Template loading
        print("\n4. Testing Template Loading...")
        from django.template.loader import get_template
        template = get_template('membership/home.html')
        print("   Template loading: ✅")
        
    except Exception as e:
        print(f"   ❌ Template error: {e}")
        traceback.print_exc()
        return False
    
    print("\n✅ All local tests passed - 500 error likely production-specific")
    print("\nPossible production issues:")
    print("- Missing environment variables")
    print("- Database connection problems")
    print("- Static files not collected")
    print("- Different Python/Django versions")
    print("- Memory/resource constraints")
    
    return True

if __name__ == "__main__":
    debug_production_500()

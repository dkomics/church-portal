#!/usr/bin/env python
"""
Web server specific debugging for production 500 errors
Tests HTTP requests through actual web server stack
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

def test_web_server_stack():
    """Test through actual web server to identify 500 error source"""
    print("=== WEB SERVER STACK DEBUGGING ===")
    
    # Test static files collection
    print("\n1. Testing Static Files...")
    try:
        from django.core.management import execute_from_command_line
        from django.conf import settings
        
        print(f"   STATIC_URL: {settings.STATIC_URL}")
        print(f"   STATIC_ROOT: {getattr(settings, 'STATIC_ROOT', 'Not set')}")
        
        # Check if static files exist
        static_files = [
            'css/home.css',
            'js/home.js',
            'images/background.jpg'
        ]
        
        from django.contrib.staticfiles.finders import find
        for file in static_files:
            found = find(file)
            print(f"   {file}: {'✅' if found else '❌'}")
            
    except Exception as e:
        print(f"   ❌ Static files error: {e}")
    
    # Test middleware stack
    print("\n2. Testing Middleware Stack...")
    try:
        from django.conf import settings
        middleware = settings.MIDDLEWARE
        print(f"   Middleware count: {len(middleware)}")
        for i, mw in enumerate(middleware, 1):
            print(f"   {i}. {mw}")
            
    except Exception as e:
        print(f"   ❌ Middleware error: {e}")
    
    # Test URL resolution
    print("\n3. Testing URL Resolution...")
    try:
        from django.urls import reverse
        from django.test import Client
        
        urls_to_test = [
            ('home', '/'),
            ('admin:index', '/admin/'),
        ]
        
        for name, expected_path in urls_to_test:
            try:
                path = reverse(name)
                print(f"   {name}: ✅ {path}")
            except Exception as url_error:
                print(f"   {name}: ❌ {url_error}")
                
    except Exception as e:
        print(f"   ❌ URL resolution error: {e}")
    
    # Test template context processors
    print("\n4. Testing Template Context Processors...")
    try:
        from django.conf import settings
        context_processors = settings.TEMPLATES[0]['OPTIONS']['context_processors']
        print(f"   Context processors count: {len(context_processors)}")
        
        for i, cp in enumerate(context_processors, 1):
            print(f"   {i}. {cp}")
            
        # Test each context processor
        from django.test import RequestFactory
        from django.contrib.auth.models import AnonymousUser
        from django.contrib.sessions.backends.db import SessionStore
        
        factory = RequestFactory()
        request = factory.get('/')
        request.session = SessionStore()
        request.user = AnonymousUser()
        
        for cp_path in context_processors:
            try:
                module_path, func_name = cp_path.rsplit('.', 1)
                module = __import__(module_path, fromlist=[func_name])
                func = getattr(module, func_name)
                result = func(request)
                print(f"   {cp_path}: ✅ {len(result) if isinstance(result, dict) else 'OK'}")
            except Exception as cp_error:
                print(f"   {cp_path}: ❌ {cp_error}")
                
    except Exception as e:
        print(f"   ❌ Context processors error: {e}")
    
    # Test database connection with production settings
    print("\n5. Testing Database Connection...")
    try:
        from django.db import connection
        from django.core.management.color import no_style
        
        # Test connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f"   Database connection: ✅ {result}")
            
        # Check database tables
        tables = connection.introspection.table_names()
        print(f"   Database tables: {len(tables)}")
        
        # Check specific tables
        required_tables = [
            'auth_user', 'auth_user_profile', 'membership_member', 
            'membership_branch', 'membership_news'
        ]
        
        for table in required_tables:
            if table in tables:
                print(f"   {table}: ✅")
            else:
                print(f"   {table}: ❌ Missing")
                
    except Exception as e:
        print(f"   ❌ Database error: {e}")
    
    print("\n6. Production Environment Analysis...")
    print(f"   Python version: {sys.version}")
    print(f"   Django version: {django.get_version()}")
    print(f"   DEBUG: {os.getenv('DEBUG', 'False')}")
    print(f"   Environment: {'Production' if os.getenv('DATABASE_URL') else 'Development'}")
    
    return True

if __name__ == "__main__":
    test_web_server_stack()

#!/usr/bin/env python
"""
Test HTTP requests to identify if 500 error is in Django or web server layer
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

from django.test import Client
from django.contrib.auth.models import User, AnonymousUser
from django.core.wsgi import get_wsgi_application
from django.test.utils import override_settings
import traceback

def test_http_layer():
    """Test HTTP layer to isolate 500 error source"""
    print("=== HTTP LAYER DEBUGGING ===")
    
    # Test 1: Django Test Client (bypasses web server)
    print("\n1. Testing Django Test Client (no web server)...")
    try:
        client = Client()
        response = client.get('/')
        print(f"   Django Test Client: ✅ Status {response.status_code}")
        
        # Test with different HTTP headers
        response = client.get('/', HTTP_HOST='jbfm-arusha.onrender.com')
        print(f"   With production host: ✅ Status {response.status_code}")
        
    except Exception as e:
        print(f"   ❌ Django Test Client error: {e}")
        traceback.print_exc()
    
    # Test 2: WSGI Application directly
    print("\n2. Testing WSGI Application...")
    try:
        application = get_wsgi_application()
        
        # Create a minimal WSGI environ
        environ = {
            'REQUEST_METHOD': 'GET',
            'PATH_INFO': '/',
            'SERVER_NAME': 'jbfm-arusha.onrender.com',
            'SERVER_PORT': '443',
            'HTTPS': 'on',
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'https',
            'wsgi.input': None,
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': True,
            'wsgi.run_once': False,
        }
        
        def start_response(status, headers, exc_info=None):
            print(f"   WSGI Response: {status}")
        
        response = application(environ, start_response)
        print(f"   WSGI Application: ✅ Response generated")
        
    except Exception as e:
        print(f"   ❌ WSGI Application error: {e}")
        traceback.print_exc()
    
    # Test 3: Template rendering with full context
    print("\n3. Testing Template Rendering...")
    try:
        from django.template.loader import render_to_string
        from django.test import RequestFactory
        from django.contrib.sessions.backends.db import SessionStore
        
        factory = RequestFactory()
        request = factory.get('/')
        request.session = SessionStore()
        request.user = AnonymousUser()
        
        # Get the actual context from the view
        from membership.views import home_page
        response = home_page(request)
        
        if hasattr(response, 'context_data'):
            context = response.context_data
        else:
            # Extract context from response
            context = {}
        
        # Try to render template with context
        html = render_to_string('membership/home.html', context, request=request)
        print(f"   Template rendering: ✅ {len(html)} characters")
        
    except Exception as e:
        print(f"   ❌ Template rendering error: {e}")
        traceback.print_exc()
    
    # Test 4: Check for specific production issues
    print("\n4. Production Environment Checks...")
    
    # Check HTTPS settings
    from django.conf import settings
    print(f"   SECURE_SSL_REDIRECT: {getattr(settings, 'SECURE_SSL_REDIRECT', False)}")
    print(f"   USE_TZ: {settings.USE_TZ}")
    print(f"   TIME_ZONE: {settings.TIME_ZONE}")
    
    # Check middleware order
    print(f"   Middleware count: {len(settings.MIDDLEWARE)}")
    
    # Check if there are any problematic middleware
    problematic_middleware = [
        'django.middleware.security.SecurityMiddleware',
        'whitenoise.middleware.WhiteNoiseMiddleware',
    ]
    
    for mw in problematic_middleware:
        if mw in settings.MIDDLEWARE:
            print(f"   {mw}: ✅ Present")
        else:
            print(f"   {mw}: ❌ Missing")
    
    # Test 5: Check for memory/resource issues
    print("\n5. Resource Usage Check...")
    try:
        import psutil
        process = psutil.Process()
        print(f"   Memory usage: {process.memory_info().rss / 1024 / 1024:.1f} MB")
        print(f"   CPU percent: {process.cpu_percent()}%")
    except ImportError:
        print("   psutil not available - cannot check resource usage")
    except Exception as e:
        print(f"   Resource check error: {e}")
    
    return True

if __name__ == "__main__":
    test_http_layer()

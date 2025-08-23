#!/usr/bin/env python
"""
Fix WSGI input stream issue that's causing 500 errors in production
"""
import os
import sys
import django
from pathlib import Path
from io import BytesIO

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_portal.settings')
django.setup()

from django.core.wsgi import get_wsgi_application
from django.test import Client
import traceback

def test_wsgi_with_proper_input():
    """Test WSGI application with proper wsgi.input stream"""
    print("=== WSGI INPUT STREAM FIX TEST ===")
    
    # Test 1: Django Test Client (should work)
    print("\n1. Testing Django Test Client...")
    try:
        client = Client()
        response = client.get('/')
        print(f"   Test Client: ✅ Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Test Client error: {e}")
    
    # Test 2: WSGI with proper input stream
    print("\n2. Testing WSGI with proper input stream...")
    try:
        application = get_wsgi_application()
        
        # Create proper WSGI environ with BytesIO input stream
        environ = {
            'REQUEST_METHOD': 'GET',
            'PATH_INFO': '/',
            'QUERY_STRING': '',
            'CONTENT_TYPE': '',
            'CONTENT_LENGTH': '0',
            'SERVER_NAME': 'jbfm-arusha.onrender.com',
            'SERVER_PORT': '443',
            'SERVER_PROTOCOL': 'HTTP/1.1',
            'HTTP_HOST': 'jbfm-arusha.onrender.com',
            'HTTP_X_FORWARDED_PROTO': 'https',
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'https',
            'wsgi.input': BytesIO(b''),  # Proper input stream
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': True,
            'wsgi.run_once': False,
        }
        
        response_data = []
        status_info = []
        
        def start_response(status, headers, exc_info=None):
            status_info.append(status)
            print(f"   WSGI Status: {status}")
            return lambda data: response_data.append(data)
        
        response_iter = application(environ, start_response)
        response_content = b''.join(response_iter)
        
        print(f"   WSGI Application: ✅ {len(response_content)} bytes")
        print(f"   Response status: {status_info[0] if status_info else 'No status'}")
        
    except Exception as e:
        print(f"   ❌ WSGI error: {e}")
        traceback.print_exc()
    
    # Test 3: Check middleware that might cause issues
    print("\n3. Testing Middleware Stack...")
    from django.conf import settings
    
    problematic_middleware = [
        'django.middleware.security.SecurityMiddleware',
        'whitenoise.middleware.WhiteNoiseMiddleware',
        'django.middleware.gzip.GZipMiddleware',
    ]
    
    for middleware in settings.MIDDLEWARE:
        is_problematic = any(prob in middleware for prob in problematic_middleware)
        status = "⚠️" if is_problematic else "✅"
        print(f"   {status} {middleware}")
    
    # Test 4: Check security settings that might interfere
    print("\n4. Checking Security Settings...")
    security_settings = [
        ('SECURE_SSL_REDIRECT', getattr(settings, 'SECURE_SSL_REDIRECT', False)),
        ('SECURE_PROXY_SSL_HEADER', getattr(settings, 'SECURE_PROXY_SSL_HEADER', None)),
        ('SECURE_HSTS_SECONDS', getattr(settings, 'SECURE_HSTS_SECONDS', 0)),
        ('DEBUG', settings.DEBUG),
    ]
    
    for setting_name, value in security_settings:
        print(f"   {setting_name}: {value}")
    
    return True

if __name__ == "__main__":
    test_wsgi_with_proper_input()

"""
Minimal test view to isolate Server Error (500) issue
"""
from django.http import HttpResponse
from django.shortcuts import render


def minimal_test(request):
    """Minimal test view to check if basic Django functionality works"""
    return HttpResponse("<h1>Test View Working</h1><p>This confirms Django is functioning.</p>")


def template_test(request):
    """Test if template rendering works"""
    try:
        return render(request, 'membership/home.html', {'stats': {'total_members': 0}})
    except Exception as e:
        return HttpResponse(f"<h1>Template Error</h1><p>Error: {str(e)}</p>")

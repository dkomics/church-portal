"""
URL configuration for church_portal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from membership.views import MemberListView, member_directory_page, MemberCreateView, register_page

urlpatterns = [
    path("admin/", admin.site.urls),

    # API endpoints
    path("api/members/", MemberListView.as_view(), name="member-list"),
    path("api/register/", MemberCreateView.as_view(), name="member-register"),

    # Front-end pages
    path("signup/", register_page, name="member-signup"),
    path("members/", member_directory_page, name="member-directory"),
]

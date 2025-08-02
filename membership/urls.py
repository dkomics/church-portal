from django.urls import path
from .views import MemberCreateView, register_page

urlpatterns = [
    path('register/', MemberCreateView.as_view(), name='member-register'),
    path('signup/', register_page, name='member-signup'),
]

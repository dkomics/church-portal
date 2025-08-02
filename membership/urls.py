from django.urls import path
from .views import MemberCreateView, MemberListView, register_page, member_directory_page

urlpatterns = [
    path('register/', MemberCreateView.as_view(), name='member-register'),
    path('signup/', register_page, name='member-signup'),
    path("api/members/", MemberListView.as_view(), name="member-list"),
    path("members/", member_directory_page, name="member-directory"),

]


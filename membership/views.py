from django.shortcuts import render
from rest_framework import generics
from .models import Member
from .serializers import MemberSerializer

def register_page(request):
    return render(request, 'membership/register.html')

def member_directory_page(request):
    return render(request, 'membership/directory.html')

class MemberCreateView(generics.CreateAPIView):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer

class MemberListView(generics.ListAPIView):
    queryset = Member.objects.all().order_by('-registration_date')
    serializer_class = MemberSerializer
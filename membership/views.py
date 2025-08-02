from django.shortcuts import render
from rest_framework import generics
from .models import Member
from .serializers import MemberSerializer

def register_page(request):
    return render(request, 'membership/register.html')

class MemberCreateView(generics.CreateAPIView):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer

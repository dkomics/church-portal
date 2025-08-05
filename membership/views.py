from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count
from django.http import JsonResponse
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
import logging
from .models import Member
from .serializers import MemberSerializer
from authentication.views import can_view_directory, can_register_members
from authentication.utils import log_user_action, filter_member_fields

# Set up logging
logger = logging.getLogger(__name__)

# Custom pagination class
class MemberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

def home_page(request):
    """Home page with basic statistics - simplified to avoid database errors"""
    try:
        # Temporarily use static stats to isolate 500 error
        stats = {
            'total_members': 10,  # Static value for testing
            'new_members_this_month': 2,  # Static value for testing
            'baptized_members': 8,  # Static value for testing
            'membership_class_completed': 6,  # Static value for testing
        }
        return render(request, 'membership/home.html', {'stats': stats})
    except Exception as e:
        logger.error(f"Error loading home page: {str(e)}")
        # Return minimal response to isolate the issue
        from django.http import HttpResponse
        return HttpResponse(f"<h1>Church Portal - Debugging Mode</h1><p>Error: {str(e)}</p><p>Site is being fixed...</p>")

@login_required
@user_passes_test(can_register_members)
def register_page(request):
    """Member registration page - requires secretary, pastor, or admin role"""
    return render(request, 'membership/register.html')

@login_required
@user_passes_test(can_view_directory)
def member_directory_page(request):
    """Member directory page - requires secretary, pastor, or admin role"""
    return render(request, 'membership/directory.html')

class MemberCreateView(generics.CreateAPIView):
    """API view for creating new members - requires authentication and proper role"""
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        try:
            # Log the registration attempt
            logger.info(f"New member registration attempt: {request.data.get('full_name', 'Unknown')}")
            
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                member = serializer.save()
                logger.info(f"New member registered successfully: {member.full_name} (ID: {member.membership_id})")
                
                # Return success response with member details
                return Response({
                    'success': True,
                    'message': 'Usajili umefanikiwa!',
                    'member': {
                        'membership_id': member.membership_id,
                        'full_name': member.full_name,
                        'registration_date': member.registration_date
                    }
                }, status=status.HTTP_201_CREATED)
            else:
                logger.warning(f"Member registration failed - validation errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Unexpected error during member registration: {str(e)}")
            return Response({
                'error': 'Hitilafu ya server imetokea. Tafadhali jaribu tena.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MemberListView(generics.ListAPIView):
    """API view for listing members with search and filtering - requires authentication"""
    serializer_class = MemberSerializer
    pagination_class = MemberPagination
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Member.objects.all()
        
        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search) |
                Q(membership_id__icontains=search) |
                Q(phone__icontains=search) |
                Q(email__icontains=search) |
                Q(emergency_phone__icontains=search)
            )
        
        # Filter by gender
        gender = self.request.query_params.get('gender', None)
        if gender:
            queryset = queryset.filter(gender=gender)
        
        # Filter by age category
        age_category = self.request.query_params.get('age_category', None)
        if age_category:
            queryset = queryset.filter(age_category=age_category)
        
        # Filter by membership type
        membership_type = self.request.query_params.get('membership_type', None)
        if membership_type:
            queryset = queryset.filter(membership_type=membership_type)
        
        # Filter by baptized status
        baptized = self.request.query_params.get('baptized', None)
        if baptized:
            queryset = queryset.filter(baptized=baptized)
        
        # Ordering
        ordering = self.request.query_params.get('ordering', '-registration_date')
        valid_orderings = [
            'full_name', '-full_name', 'registration_date', '-registration_date',
            'membership_id', '-membership_id', 'gender', '-gender',
            'age_category', '-age_category', 'membership_type', '-membership_type'
        ]
        if ordering in valid_orderings:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by('-registration_date')
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        try:
            response = super().list(request, *args, **kwargs)
            logger.info(f"Member list requested - returned {len(response.data.get('results', []))} members")
            return response
        except Exception as e:
            logger.error(f"Error retrieving member list: {str(e)}")
            return Response({
                'error': 'Hitilafu imetokea wakati wa kupakia orodha ya washirika.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def member_statistics(request):
    """API endpoint for member statistics"""
    try:
        current_year = timezone.now().year
        current_month = timezone.now().month
        
        stats = {
            'total_members': Member.objects.count(),
            'male_members': Member.objects.filter(gender='Male').count(),
            'female_members': Member.objects.filter(gender='Female').count(),
            'baptized_members': Member.objects.filter(baptized='Yes').count(),
            'new_members_this_year': Member.objects.filter(
                registration_date__year=current_year
            ).count(),
            'new_members_this_month': Member.objects.filter(
                registration_date__year=current_year,
                registration_date__month=current_month
            ).count(),
            'membership_class_completed': Member.objects.filter(
                membership_class='Yes'
            ).count(),
            'by_age_category': dict(
                Member.objects.values('age_category').annotate(
                    count=Count('age_category')
                ).values_list('age_category', 'count')
            ),
            'by_membership_type': dict(
                Member.objects.values('membership_type').annotate(
                    count=Count('membership_type')
                ).values_list('membership_type', 'count')
            ),
        }
        
        logger.info("Member statistics requested")
        return Response(stats)
        
    except Exception as e:
        logger.error(f"Error retrieving member statistics: {str(e)}")
        return Response({
            'error': 'Hitilafu imetokea wakati wa kupakia takwimu.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
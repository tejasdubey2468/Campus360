from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Count
from .models import SystemLog, ActivityLog, AdminApproval
from .serializers import SystemLogSerializer, ActivityLogSerializer, AdminApprovalSerializer


class SystemLogListView(generics.ListAPIView):
    queryset = SystemLog.objects.select_related('user').all()
    serializer_class = SystemLogSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['action', 'user', 'entity_type']


class ActivityLogListView(generics.ListAPIView):
    queryset = ActivityLog.objects.select_related('user').all()
    serializer_class = ActivityLogSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['module', 'user']


class AdminApprovalListView(generics.ListCreateAPIView):
    queryset = AdminApproval.objects.select_related('admin').all()
    serializer_class = AdminApprovalSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['status', 'entity_type']


@api_view(['GET'])
@permission_classes([AllowAny])
def get_admin_analytics(request):
    """Get high-level system analytics for the admin dashboard."""
    # This is a sample analytics aggregator
    analytics = {
        'total_logs': SystemLog.objects.count(),
        'pending_approvals': AdminApproval.objects.filter(status='PENDING').count(),
        'activity_by_module': ActivityLog.objects.values('module').annotate(count=Count('id')),
        'recent_actions': SystemLogSerializer(SystemLog.objects.all()[:10], many=True).data
    }
    return Response(analytics)

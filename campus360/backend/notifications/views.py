from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone
from .models import Notification, UserNotification
from .serializers import NotificationSerializer, UserNotificationSerializer


class NotificationListView(generics.ListCreateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        # Allow global and targeted notifications
        return Notification.objects.filter(is_active=True).order_by('-created_at')


class UserNotificationListView(generics.ListAPIView):
    serializer_class = UserNotificationSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if not user_id:
            return UserNotification.objects.none()
        return UserNotification.objects.filter(user_id=user_id).select_related('notification').order_by('-created_at')


@api_view(['PATCH'])
@permission_classes([AllowAny])
def mark_notification_read(request, un_id):
    """Mark a specific user notification as read."""
    try:
        un = UserNotification.objects.get(id=un_id)
        un.is_read = True
        un.read_at = timezone.now()
        un.save()
        return Response({'message': 'Marked as read'})
    except UserNotification.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)

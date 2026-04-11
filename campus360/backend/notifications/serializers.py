from rest_framework import serializers
from .models import Notification, UserNotification


class NotificationSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = '__all__'

    def get_sender_name(self, obj):
        return obj.sender.full_name if obj.sender else "System"


class UserNotificationSerializer(serializers.ModelSerializer):
    notification_details = NotificationSerializer(source='notification', read_only=True)

    class Meta:
        model = UserNotification
        fields = '__all__'

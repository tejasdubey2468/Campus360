from rest_framework import serializers
from .models import SystemLog, ActivityLog, AdminApproval


class SystemLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = SystemLog
        fields = '__all__'


class ActivityLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = ActivityLog
        fields = '__all__'


class AdminApprovalSerializer(serializers.ModelSerializer):
    admin_name = serializers.CharField(source='admin.full_name', read_only=True)

    class Meta:
        model = AdminApproval
        fields = '__all__'

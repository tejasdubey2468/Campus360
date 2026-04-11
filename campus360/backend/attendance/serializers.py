from rest_framework import serializers
from .models import QRSession, Attendance, AttendanceSummary


class QRSessionSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True, default=None)
    faculty_name = serializers.CharField(source='faculty.profile.full_name', read_only=True, default=None)

    class Meta:
        model = QRSession
        fields = '__all__'


class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.profile.full_name', read_only=True, default=None)
    subject_name = serializers.CharField(source='subject.name', read_only=True, default=None)

    class Meta:
        model = Attendance
        fields = '__all__'


class AttendanceSummarySerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True, default=None)
    student_name = serializers.CharField(source='student.profile.full_name', read_only=True, default=None)

    class Meta:
        model = AttendanceSummary
        fields = '__all__'


class QRScanSerializer(serializers.Serializer):
    qr_code_data = serializers.CharField()
    student_id = serializers.UUIDField()

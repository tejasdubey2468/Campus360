from rest_framework import serializers
from .models import TimetableSlot


class TimetableSlotSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True, default=None)
    subject_code = serializers.CharField(source='subject.code', read_only=True, default=None)
    faculty_name = serializers.CharField(source='faculty.profile.full_name', read_only=True, default=None)
    classroom_name = serializers.CharField(source='classroom.name', read_only=True, default=None)
    department_name = serializers.CharField(source='department.name', read_only=True, default=None)

    class Meta:
        model = TimetableSlot
        fields = '__all__'

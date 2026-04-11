from rest_framework import serializers
from .models import Classroom, ClassroomBooking


class ClassroomSerializer(serializers.ModelSerializer):
    current_faculty_name = serializers.CharField(source='current_faculty.profile.full_name', read_only=True)

    class Meta:
        model = Classroom
        fields = '__all__'


class ClassroomBookingSerializer(serializers.ModelSerializer):
    classroom_name = serializers.CharField(source='classroom.name', read_only=True)
    booked_by_name = serializers.CharField(source='booked_by.full_name', read_only=True)

    class Meta:
        model = ClassroomBooking
        fields = '__all__'

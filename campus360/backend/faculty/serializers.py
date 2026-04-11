from rest_framework import serializers
from .models import Faculty, FacultySubject
from accounts.serializers import ProfileSerializer


class FacultySerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True, default=None)

    class Meta:
        model = Faculty
        fields = '__all__'


class FacultySubjectSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True, default=None)
    faculty_name = serializers.CharField(source='faculty.profile.full_name', read_only=True, default=None)

    class Meta:
        model = FacultySubject
        fields = '__all__'

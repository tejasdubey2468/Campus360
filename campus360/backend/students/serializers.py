from rest_framework import serializers
from .models import Student, Subject, Marks, SemesterResult
from accounts.serializers import ProfileSerializer


class SubjectSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True, default=None)

    class Meta:
        model = Subject
        fields = '__all__'


class StudentSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True, default=None)

    class Meta:
        model = Student
        fields = '__all__'


class MarksSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True, default=None)

    class Meta:
        model = Marks
        fields = '__all__'


class SemesterResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = SemesterResult
        fields = '__all__'


class StudentDashboardSerializer(serializers.Serializer):
    profile = ProfileSerializer()
    student = StudentSerializer()
    semester_results = SemesterResultSerializer(many=True)
    recent_marks = MarksSerializer(many=True)

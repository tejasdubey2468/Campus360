from rest_framework import serializers
from .models import Assignment, StudentSubmission, Note


class AssignmentSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    faculty_name = serializers.CharField(source='faculty.profile.full_name', read_only=True)

    class Meta:
        model = Assignment
        fields = '__all__'


class StudentSubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.profile.full_name', read_only=True)
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)

    class Meta:
        model = StudentSubmission
        fields = '__all__'


class NoteSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    faculty_name = serializers.CharField(source='faculty.profile.full_name', read_only=True)

    class Meta:
        model = Note
        fields = '__all__'

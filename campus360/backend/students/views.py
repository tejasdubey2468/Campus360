from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Student, Subject, Marks, SemesterResult
from .serializers import StudentSerializer, SubjectSerializer, MarksSerializer, SemesterResultSerializer
from accounts.models import Profile


@api_view(['GET'])
@permission_classes([AllowAny])
def student_dashboard(request, profile_id):
    """Get complete student dashboard data."""
    try:
        profile = Profile.objects.select_related('department').get(id=profile_id)
        student = Student.objects.select_related('department').get(profile_id=profile_id)
        semester_results = SemesterResult.objects.filter(student=student).order_by('-semester')
        recent_marks = Marks.objects.filter(student=student).select_related('subject').order_by('-created_at')[:10]

        return Response({
            'profile': {
                'id': str(profile.id),
                'full_name': profile.full_name,
                'email': profile.email,
                'phone': profile.phone,
                'avatar_url': profile.avatar_url,
                'role': profile.role,
            },
            'student': StudentSerializer(student).data,
            'semester_results': SemesterResultSerializer(semester_results, many=True).data,
            'recent_marks': MarksSerializer(recent_marks, many=True).data,
        })
    except Profile.DoesNotExist:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
    except Student.DoesNotExist:
        return Response({'error': 'Student record not found'}, status=status.HTTP_404_NOT_FOUND)


class StudentListView(generics.ListCreateAPIView):
    queryset = Student.objects.select_related('profile', 'department').all()
    serializer_class = StudentSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['department', 'year', 'semester', 'fees_status']
    search_fields = ['roll_number', 'student_id', 'profile__full_name']


class StudentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.select_related('profile', 'department').all()
    serializer_class = StudentSerializer
    permission_classes = [AllowAny]


class SubjectListView(generics.ListCreateAPIView):
    queryset = Subject.objects.filter(is_active=True).select_related('department')
    serializer_class = SubjectSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['department', 'semester', 'subject_type']
    search_fields = ['name', 'code']


class MarksListView(generics.ListCreateAPIView):
    serializer_class = MarksSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = Marks.objects.select_related('subject', 'student').all()
        student_id = self.request.query_params.get('student_id')
        semester = self.request.query_params.get('semester')
        if student_id:
            qs = qs.filter(student_id=student_id)
        if semester:
            qs = qs.filter(semester=semester)
        return qs


class SemesterResultListView(generics.ListCreateAPIView):
    serializer_class = SemesterResultSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = SemesterResult.objects.all()
        student_id = self.request.query_params.get('student_id')
        if student_id:
            qs = qs.filter(student_id=student_id)
        return qs.order_by('-semester')

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Faculty, FacultySubject
from .serializers import FacultySerializer, FacultySubjectSerializer
from accounts.models import Profile
from accounts.serializers import ProfileSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def faculty_dashboard(request, profile_id):
    """Get complete faculty dashboard data."""
    try:
        profile = Profile.objects.select_related('department').get(id=profile_id)
        faculty = Faculty.objects.select_related('department').get(profile_id=profile_id)
        assigned_subjects = FacultySubject.objects.filter(faculty=faculty).select_related('subject')

        return Response({
            'profile': ProfileSerializer(profile).data,
            'faculty': FacultySerializer(faculty).data,
            'assigned_subjects': FacultySubjectSerializer(assigned_subjects, many=True).data,
        })
    except (Profile.DoesNotExist, Faculty.DoesNotExist) as e:
        return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)


class FacultyListView(generics.ListCreateAPIView):
    queryset = Faculty.objects.select_related('profile', 'department').all()
    serializer_class = FacultySerializer
    permission_classes = [AllowAny]
    filterset_fields = ['department', 'designation']
    search_fields = ['faculty_id', 'profile__full_name', 'specialization']


class FacultyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Faculty.objects.select_related('profile', 'department').all()
    serializer_class = FacultySerializer
    permission_classes = [AllowAny]


class FacultySubjectListView(generics.ListCreateAPIView):
    serializer_class = FacultySubjectSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = FacultySubject.objects.select_related('faculty__profile', 'subject').all()
        faculty_id = self.request.query_params.get('faculty_id')
        if faculty_id:
            qs = qs.filter(faculty_id=faculty_id)
        return qs

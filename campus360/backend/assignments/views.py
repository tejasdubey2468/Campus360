from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from campus360_api.supabase_client import upload_to_supabase
from .models import Assignment, StudentSubmission, Note
from .serializers import AssignmentSerializer, StudentSubmissionSerializer, NoteSerializer


class AssignmentListView(generics.ListCreateAPIView):
    serializer_class = AssignmentSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = Assignment.objects.filter(is_active=True).select_related('subject', 'faculty__profile')
        faculty_id = self.request.query_params.get('faculty_id')
        subject_id = self.request.query_params.get('subject_id')
        semester = self.request.query_params.get('semester')
        if faculty_id:
            qs = qs.filter(faculty_id=faculty_id)
        if subject_id:
            qs = qs.filter(subject_id=subject_id)
        if semester:
            qs = qs.filter(semester=semester)
        return qs


@api_view(['POST'])
@permission_classes([AllowAny])
def upload_assignment_file(request, assignment_id):
    """Upload an assignment document to Supabase Storage."""
    if 'file' not in request.FILES:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    file = request.FILES['file']
    file_path = f"assignments/{assignment_id}/{file.name}"
    
    try:
        public_url = upload_to_supabase('assignments', file_path, file.read(), file.content_type)
        Assignment.objects.filter(id=assignment_id).update(file_url=public_url)
        return Response({'file_url': public_url})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SubmissionListView(generics.ListCreateAPIView):
    serializer_class = StudentSubmissionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = StudentSubmission.objects.select_related('assignment', 'student__profile')
        assignment_id = self.request.query_params.get('assignment_id')
        student_id = self.request.query_params.get('student_id')
        if assignment_id:
            qs = qs.filter(assignment_id=assignment_id)
        if student_id:
            qs = qs.filter(student_id=student_id)
        return qs


@api_view(['POST'])
@permission_classes([AllowAny])
def submit_assignment(request):
    """Submit an assignment with file upload to Supabase."""
    assignment_id = request.data.get('assignment_id')
    student_id = request.data.get('student_id')
    
    if not assignment_id or not student_id:
        return Response({'error': 'assignment_id and student_id are required'}, status=status.HTTP_400_BAD_REQUEST)
        
    if 'file' not in request.FILES:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
    file = request.FILES['file']
    file_path = f"submissions/{assignment_id}/{student_id}/{file.name}"
    
    try:
        public_url = upload_to_supabase('assignments', file_path, file.read(), file.content_type)
        submission = StudentSubmission.objects.create(
            assignment_id=assignment_id,
            student_id=student_id,
            file_url=public_url,
            status='PENDING'
        )
        return Response(StudentSubmissionSerializer(submission).data, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NoteListView(generics.ListCreateAPIView):
    serializer_class = NoteSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = Note.objects.filter(is_active=True).select_related('subject', 'faculty__profile')
        subject_id = self.request.query_params.get('subject_id')
        semester = self.request.query_params.get('semester')
        if subject_id:
            qs = qs.filter(subject_id=subject_id)
        if semester:
            qs = qs.filter(semester=semester)
        return qs

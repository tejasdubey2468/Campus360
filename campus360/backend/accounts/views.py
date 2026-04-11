from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
from campus360_api.supabase_client import get_supabase_client, upload_to_supabase
from .models import Profile, Department
from .serializers import ProfileSerializer, DepartmentSerializer, RegisterSerializer, LoginSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Register a new user via Supabase Auth and create a profile."""
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    try:
        client = get_supabase_client()
        auth_response = client.auth.sign_up({
            'email': data['email'],
            'password': data['password'],
            'options': {
                'data': {
                    'full_name': data['full_name'],
                    'role': data['role'],
                }
            }
        })

        if auth_response.user:
            return Response({
                'message': 'Registration successful',
                'user_id': str(auth_response.user.id),
                'email': data['email'],
            }, status=status.HTTP_201_CREATED)

        return Response({'error': 'Registration failed'}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Login via Supabase Auth and return session tokens."""
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    try:
        client = get_supabase_client()
        auth_response = client.auth.sign_in_with_password({
            'email': data['email'],
            'password': data['password'],
        })

        if auth_response.session:
            user = auth_response.user
            # Ensure profile exists (sync case)
            profile, created = Profile.objects.get_or_create(
                id=user.id,
                defaults={
                    'email': user.email,
                    'full_name': user.user_metadata.get('full_name', ''),
                    'role': user.user_metadata.get('role', 'student'),
                }
            )
            
            # If exists but role was missing (e.g. manual signup), sync it
            if not created and not profile.full_name:
                profile.full_name = user.user_metadata.get('full_name', '')
                profile.role = user.user_metadata.get('role', profile.role)
                profile.save()

            # --- AUTO-SYNC STUDENT/FACULTY RECORDS ---
            if profile.role == 'student':
                from students.models import Student
                from django.utils.crypto import get_random_string
                if not Student.objects.filter(profile=profile).exists():
                    dept = profile.department or Department.objects.first()
                    if dept:
                        # Auto-create student record if missing
                        roll = f"C360-{get_random_string(4).upper()}"
                        Student.objects.create(
                            id=profile.id, # Force same ID
                            profile=profile,
                            department=dept,
                            roll_number=roll,
                            student_id=roll,
                            year=1,
                            semester=1,
                            cgpa=8.0 # Default starting
                        )
            elif profile.role == 'faculty':
                from faculty.models import Faculty
                if not Faculty.objects.filter(profile=profile).exists():
                    dept = profile.department or Department.objects.first()
                    if dept:
                        fid = f"F-{profile.full_name[:3].upper()}"
                        Faculty.objects.create(
                            id=profile.id, # Force same ID
                            profile=profile,
                            department=dept,
                            faculty_id=fid,
                            designation="Assistant Professor"
                        )
            # ----------------------------------------

            profile_data = ProfileSerializer(profile).data

            return Response({
                'access_token': auth_response.session.access_token,
                'refresh_token': auth_response.session.refresh_token,
                'expires_in': auth_response.session.expires_in,
                'user': profile_data,
            })

        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    except Exception as e:
        error_msg = str(e)
        if "Invalid login credentials" in error_msg:
             return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({'error': error_msg}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([AllowAny])
def logout(request):
    """Logout and invalidate the Supabase session."""
    try:
        client = get_supabase_client()
        client.auth.sign_out()
        return Response({'message': 'Logged out successfully'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH'])
@permission_classes([AllowAny])
def profile_view(request, profile_id=None):
    """Get or update a user profile."""
    if request.method == 'GET':
        if not profile_id:
            return Response({'error': 'Profile ID required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            profile = Profile.objects.select_related('department').get(id=profile_id)
            return Response(ProfileSerializer(profile).data)
        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

    elif request.method == 'PATCH':
        try:
            profile = Profile.objects.get(id=profile_id)
            serializer = ProfileSerializer(profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
def upload_avatar(request, profile_id):
    """Upload a profile avatar to Supabase Storage."""
    if 'file' not in request.FILES:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

    file = request.FILES['file']
    file_path = f"avatars/{profile_id}/{file.name}"

    try:
        public_url = upload_to_supabase('profile-images', file_path, file.read(), file.content_type)
        Profile.objects.filter(id=profile_id).update(avatar_url=public_url)
        return Response({'avatar_url': public_url})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DepartmentListView(generics.ListCreateAPIView):
    queryset = Department.objects.filter(is_active=True)
    serializer_class = DepartmentSerializer
    permission_classes = [AllowAny]
    search_fields = ['name', 'code']

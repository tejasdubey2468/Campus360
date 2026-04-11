from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Classroom, ClassroomBooking
from .serializers import ClassroomSerializer, ClassroomBookingSerializer


class ClassroomListView(generics.ListAPIView):
    queryset = Classroom.objects.filter(is_active=True)
    serializer_class = ClassroomSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['room_type', 'building', 'status']
    search_fields = ['name', 'building']


class ClassroomDetailView(generics.RetrieveAPIView):
    queryset = Classroom.objects.filter(is_active=True)
    serializer_class = ClassroomSerializer
    permission_classes = [AllowAny]


@api_view(['POST'])
@permission_classes([AllowAny])
def book_classroom(request):
    """Book a classroom for a specific slot."""
    serializer = ClassroomBookingSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    # Check for slot conflicts
    classroom = serializer.validated_data['classroom']
    date = serializer.validated_data['booking_date']
    start = serializer.validated_data['start_time']
    end = serializer.validated_data['end_time']
    
    conflicts = ClassroomBooking.objects.filter(
        classroom=classroom,
        booking_date=date,
        status__in=['PENDING', 'APPROVED'],
        start_time__lt=end,
        end_time__gt=start
    ).exists()
    
    if conflicts:
        return Response({'error': 'Time slot conflict with existing booking'}, status=status.HTTP_409_CONFLICT)
        
    booking = serializer.save(status='PENDING')
    return Response(ClassroomBookingSerializer(booking).data, status=status.HTTP_201_CREATED)


class StudentBookingListView(generics.ListAPIView):
    serializer_class = ClassroomBookingSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if not user_id:
            return ClassroomBooking.objects.none()
        return ClassroomBooking.objects.filter(booked_by_id=user_id).select_related('classroom').order_by('-booking_date')

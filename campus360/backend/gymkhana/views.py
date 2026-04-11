from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Sport, Equipment, EquipmentBooking, Turf, TurfBooking
from .serializers import (
    SportSerializer, EquipmentSerializer, EquipmentBookingSerializer,
    TurfSerializer, TurfBookingSerializer
)


class SportListView(generics.ListAPIView):
    queryset = Sport.objects.filter(is_active=True)
    serializer_class = SportSerializer
    permission_classes = [AllowAny]


class EquipmentListView(generics.ListAPIView):
    queryset = Equipment.objects.filter(is_active=True).select_related('sport')
    serializer_class = EquipmentSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['category', 'sport']


@api_view(['POST'])
@permission_classes([AllowAny])
def book_equipment(request):
    """Book a piece of sports equipment. student field is optional (guest bookings)."""
    # Build payload, making student optional
    data = request.data.copy()

    serializer = EquipmentBookingSerializer(data=data)
    if not serializer.is_valid():
        # Try without student field if it fails validation
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    equipment = serializer.validated_data['equipment']
    requested_qty = serializer.validated_data.get('quantity', 1)

    if equipment.available_quantity < requested_qty:
        return Response({'error': 'Insufficient equipment available'}, status=status.HTTP_400_BAD_REQUEST)

    booking = serializer.save(status='PENDING')

    equipment.available_quantity -= requested_qty
    equipment.save()

    return Response(EquipmentBookingSerializer(booking).data, status=status.HTTP_201_CREATED)


class EquipmentBookingListView(generics.ListAPIView):
    """List all equipment bookings, optionally filtered by student_name or roll_number."""
    serializer_class = EquipmentBookingSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = EquipmentBooking.objects.select_related('equipment').all().order_by('-created_at')
        student_name = self.request.query_params.get('student_name')
        roll_number = self.request.query_params.get('roll_number')
        student_id = self.request.query_params.get('student_id')
        if student_name:
            qs = qs.filter(student_name__icontains=student_name)
        if roll_number:
            qs = qs.filter(roll_number=roll_number)
        if student_id:
            qs = qs.filter(student_id=student_id)
        return qs


class EquipmentBookingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = EquipmentBooking.objects.all()
    serializer_class = EquipmentBookingSerializer
    permission_classes = [AllowAny]


class TurfListView(generics.ListAPIView):
    queryset = Turf.objects.filter(is_active=True).select_related('sport')
    serializer_class = TurfSerializer
    permission_classes = [AllowAny]


@api_view(['POST'])
@permission_classes([AllowAny])
def book_turf(request):
    """Book a sports turf/ground."""
    data = request.data.copy()

    serializer = TurfBookingSerializer(data=data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    turf = serializer.validated_data['turf']
    booking_date = serializer.validated_data['booking_date']
    slot = serializer.validated_data['time_slot']

    existing = TurfBooking.objects.filter(
        turf=turf,
        booking_date=booking_date,
        time_slot=slot,
        status__in=['PENDING', 'APPROVED']
    ).exists()
    if existing:
        return Response({'error': 'Slot already booked'}, status=status.HTTP_409_CONFLICT)

    booking = serializer.save(status='PENDING')
    return Response(TurfBookingSerializer(booking).data, status=status.HTTP_201_CREATED)


class TurfBookingListView(generics.ListAPIView):
    """List all turf bookings, optionally filtered."""
    serializer_class = TurfBookingSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = TurfBooking.objects.select_related('turf').all().order_by('-created_at')
        student_name = self.request.query_params.get('student_name')
        roll_number = self.request.query_params.get('roll_number')
        student_id = self.request.query_params.get('student_id')
        if student_name:
            qs = qs.filter(student_name__icontains=student_name)
        if roll_number:
            qs = qs.filter(roll_number=roll_number)
        if student_id:
            qs = qs.filter(student_id=student_id)
        return qs


class TurfBookingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TurfBooking.objects.all()
    serializer_class = TurfBookingSerializer
    permission_classes = [AllowAny]


class StudentBookingsView(generics.ListAPIView):
    """Get all bookings for a specific student."""
    permission_classes = [AllowAny]

    def get(self, request, student_id):
        equipment_bookings = EquipmentBooking.objects.filter(student_id=student_id).select_related('equipment')
        turf_bookings = TurfBooking.objects.filter(student_id=student_id).select_related('turf')

        return Response({
            'equipment': EquipmentBookingSerializer(equipment_bookings, many=True).data,
            'turfs': TurfBookingSerializer(turf_bookings, many=True).data
        })

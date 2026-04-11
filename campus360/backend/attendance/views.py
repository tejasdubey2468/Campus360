import uuid
import qrcode
import io
import base64
from datetime import date, timedelta
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from campus360_api.supabase_client import upload_to_supabase
from .models import QRSession, Attendance, AttendanceSummary
from .serializers import QRSessionSerializer, AttendanceSerializer, AttendanceSummarySerializer, QRScanSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def generate_qr(request):
    """Faculty generates a QR code for a lecture session."""
    faculty_id = request.data.get('faculty_id')
    subject_id = request.data.get('subject_id')
    timetable_slot_id = request.data.get('timetable_slot_id')
    duration_minutes = int(request.data.get('duration_minutes', 15))

    if not all([faculty_id, subject_id, timetable_slot_id]):
        return Response({'error': 'faculty_id, subject_id, and timetable_slot_id are required'}, status=status.HTTP_400_BAD_REQUEST)

    # Generate unique QR data
    qr_token = str(uuid.uuid4())
    qr_data = f"CAMPUS360_ATT|{qr_token}|{subject_id}|{faculty_id}"

    now = timezone.now()
    valid_until = now + timedelta(minutes=duration_minutes)

    # Generate QR image
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    # Upload to Supabase Storage
    file_path = f"qr-codes/{faculty_id}/{qr_token}.png"
    try:
        qr_image_url = upload_to_supabase('qr-codes', file_path, buffer.read(), 'image/png')
    except Exception:
        qr_image_url = None

    # Also return base64 for immediate display
    buffer.seek(0)
    qr_base64 = base64.b64encode(buffer.read()).decode('utf-8')

    # Create QR session record
    session = QRSession.objects.create(
        timetable_slot_id=timetable_slot_id,
        faculty_id=faculty_id,
        subject_id=subject_id,
        qr_code_data=qr_data,
        qr_image_url=qr_image_url,
        session_date=date.today(),
        valid_from=now,
        valid_until=valid_until,
        is_active=True,
    )

    return Response({
        'session_id': str(session.id),
        'qr_code_data': qr_data,
        'qr_image_url': qr_image_url,
        'qr_base64': f"data:image/png;base64,{qr_base64}",
        'valid_from': now.isoformat(),
        'valid_until': valid_until.isoformat(),
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def scan_qr(request):
    """Student scans QR code to mark attendance."""
    serializer = QRScanSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    qr_code_data = serializer.validated_data['qr_code_data']
    student_id = serializer.validated_data['student_id']

    # Find active QR session
    try:
        session = QRSession.objects.get(qr_code_data=qr_code_data, is_active=True)
    except QRSession.DoesNotExist:
        return Response({'error': 'Invalid or expired QR code'}, status=status.HTTP_400_BAD_REQUEST)

    now = timezone.now()
    if now > session.valid_until:
        return Response({'error': 'QR code has expired'}, status=status.HTTP_400_BAD_REQUEST)

    # Check for duplicate scan
    existing = Attendance.objects.filter(
        student_id=student_id,
        qr_session=session,
    ).exists()

    if existing:
        return Response({'error': 'Attendance already recorded for this session'}, status=status.HTTP_409_CONFLICT)

    # Record attendance
    attendance = Attendance.objects.create(
        student_id=student_id,
        faculty_id=session.faculty_id,
        subject_id=session.subject_id,
        timetable_slot_id=session.timetable_slot_id,
        qr_session=session,
        attendance_date=date.today(),
        status='PRESENT',
    )

    return Response({
        'message': 'Attendance recorded successfully',
        'attendance_id': str(attendance.id),
        'subject': session.subject.name if session.subject else None,
        'status': 'PRESENT',
    }, status=status.HTTP_201_CREATED)


class AttendanceListView(generics.ListCreateAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = Attendance.objects.select_related('student__profile', 'subject', 'faculty__profile').all()
        student_id = self.request.query_params.get('student_id')
        subject_id = self.request.query_params.get('subject_id')
        att_date = self.request.query_params.get('date')
        if student_id:
            qs = qs.filter(student_id=student_id)
        if subject_id:
            qs = qs.filter(subject_id=subject_id)
        if att_date:
            qs = qs.filter(attendance_date=att_date)
        return qs.order_by('-attendance_date')


class AttendanceSummaryListView(generics.ListAPIView):
    serializer_class = AttendanceSummarySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = AttendanceSummary.objects.select_related('student__profile', 'subject').all()
        student_id = self.request.query_params.get('student_id')
        if student_id:
            qs = qs.filter(student_id=student_id)
        return qs


class QRSessionListView(generics.ListAPIView):
    serializer_class = QRSessionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = QRSession.objects.select_related('subject', 'faculty__profile').all()
        faculty_id = self.request.query_params.get('faculty_id')
        if faculty_id:
            qs = qs.filter(faculty_id=faculty_id)
        return qs.order_by('-session_date')

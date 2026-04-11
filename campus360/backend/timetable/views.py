from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import TimetableSlot
from .serializers import TimetableSlotSerializer


class TimetableSlotListView(generics.ListCreateAPIView):
    serializer_class = TimetableSlotSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = TimetableSlot.objects.filter(is_active=True).select_related(
            'subject', 'faculty__profile', 'classroom', 'department'
        )
        department_id = self.request.query_params.get('department_id')
        faculty_id = self.request.query_params.get('faculty_id')
        semester = self.request.query_params.get('semester')
        day = self.request.query_params.get('day')
        if department_id:
            qs = qs.filter(department_id=department_id)
        if faculty_id:
            qs = qs.filter(faculty_id=faculty_id)
        if semester:
            qs = qs.filter(semester=semester)
        if day:
            qs = qs.filter(day=day.upper())
        return qs.order_by('day', 'start_time')


class TimetableSlotDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TimetableSlot.objects.select_related('subject', 'faculty__profile', 'classroom', 'department')
    serializer_class = TimetableSlotSerializer
    permission_classes = [AllowAny]

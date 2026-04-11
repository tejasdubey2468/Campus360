from django.urls import path
from . import views

urlpatterns = [
    path('qr/generate/', views.generate_qr, name='generate-qr'),
    path('qr/scan/', views.scan_qr, name='scan-qr'),
    path('qr/sessions/', views.QRSessionListView.as_view(), name='qr-sessions'),
    path('records/', views.AttendanceListView.as_view(), name='attendance-list'),
    path('summary/', views.AttendanceSummaryListView.as_view(), name='attendance-summary'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('sports/', views.SportListView.as_view(), name='sport-list'),
    path('equipment/', views.EquipmentListView.as_view(), name='equipment-list'),
    path('equipment/book/', views.book_equipment, name='book-equipment'),
    path('equipment-bookings/', views.EquipmentBookingListView.as_view(), name='equipment-booking-list'),
    path('equipment-bookings/<uuid:pk>/', views.EquipmentBookingDetailView.as_view(), name='equipment-booking-detail'),
    path('turfs/', views.TurfListView.as_view(), name='turf-list'),
    path('turf/book/', views.book_turf, name='book-turf'),
    path('turf-bookings/', views.TurfBookingListView.as_view(), name='turf-booking-list'),
    path('turf-bookings/<uuid:pk>/', views.TurfBookingDetailView.as_view(), name='turf-booking-detail'),
    path('bookings/<uuid:student_id>/', views.StudentBookingsView.as_view(), name='student-bookings'),
]

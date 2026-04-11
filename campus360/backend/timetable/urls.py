from django.urls import path
from . import views

urlpatterns = [
    path('slots/', views.TimetableSlotListView.as_view(), name='timetable-slot-list'),
    path('slots/<uuid:pk>/', views.TimetableSlotDetailView.as_view(), name='timetable-slot-detail'),
]

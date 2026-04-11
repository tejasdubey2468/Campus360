from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/<uuid:profile_id>/', views.faculty_dashboard, name='faculty-dashboard'),
    path('list/', views.FacultyListView.as_view(), name='faculty-list'),
    path('<uuid:pk>/', views.FacultyDetailView.as_view(), name='faculty-detail'),
    path('subjects/', views.FacultySubjectListView.as_view(), name='faculty-subject-list'),
]

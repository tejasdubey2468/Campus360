# scheduler/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # Timetable generation and viewing dashboards
    path('generate/', views.generate_timetable_dashboard, name='generate_timetable_dashboard'),
    path('view/', views.view_timetable_dashboard, name='view_timetable_dashboard'),
    
    # Timetable detail views
    path('timetable/<int:pk>/', views.view_timetable, name='view_timetable'),
    path('timetable/<int:pk>/detail/', views.view_timetable, name='timetable_detail'),  # Alias
    path('timetable/<int:pk>/activate/', views.activate_timetable, name='activate_timetable'),
    path('timetable/<int:pk>/api/', views.api_timetable_data, name='api_timetable_data'),
    
    # Class and teacher timetables
    path('class/<int:class_id>/timetable/', views.class_timetable, name='class_timetable'),
    path('teacher/<int:teacher_id>/timetable/', views.teacher_timetable, name='teacher_timetable'),
    
    # Data management
    path('manage/', views.manage_data, name='manage_data'),
    path('timetables/', views.view_timetables, name='view_timetables'),  # Alias for backward compatibility
]

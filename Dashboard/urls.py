from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('report/', views.attendance_report, name='attendance_report'),
]
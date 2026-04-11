from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/<uuid:profile_id>/', views.student_dashboard, name='student-dashboard'),
    path('list/', views.StudentListView.as_view(), name='student-list'),
    path('<uuid:pk>/', views.StudentDetailView.as_view(), name='student-detail'),
    path('subjects/', views.SubjectListView.as_view(), name='subject-list'),
    path('marks/', views.MarksListView.as_view(), name='marks-list'),
    path('results/', views.SemesterResultListView.as_view(), name='results-list'),
]

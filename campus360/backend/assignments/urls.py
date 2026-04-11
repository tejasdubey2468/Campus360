from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.AssignmentListView.as_view(), name='assignment-list'),
    path('<uuid:assignment_id>/upload/', views.upload_assignment_file, name='upload-assignment-file'),
    path('submissions/', views.SubmissionListView.as_view(), name='submission-list'),
    path('submit/', views.submit_assignment, name='submit-assignment'),
    path('notes/', views.NoteListView.as_view(), name='note-list'),
]

from . import views
from django.urls import path

urlpatterns = [
    path("", views.add_manually, name="student_add_manually"),
    path("submit/", views.add_manually_post, name="student_add_manually_post"),
    path("submitted/", views.submitted, name="student_submitted"),
]

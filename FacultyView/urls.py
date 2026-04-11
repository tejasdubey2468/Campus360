from . import views
from django.urls import path

urlpatterns = [
    path("", views.faculty_view, name="faculty_view"),
]

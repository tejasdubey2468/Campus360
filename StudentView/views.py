from django.shortcuts import render
from FacultyView.models import Student
from django.http import HttpResponseRedirect
from django.urls import reverse
from attendance_state import present

# Create your views here.


def add_manually(request):
    if request.method == "GET":
        return render(request, "StudentView/StudentViewIndex.html")


def add_manually_post(request):
    student_roll = request.POST["student-name"].strip()
    if student_roll.isdigit() and 101 <= int(student_roll) <= 200:
        present.add(student_roll)
        return HttpResponseRedirect(reverse("student_submitted"))

    try:
        Student.objects.get(s_roll=student_roll)
        present.add(student_roll)
        return HttpResponseRedirect(reverse("student_submitted"))
    except Student.DoesNotExist:
        return render(
            request,
            "StudentView/StudentViewIndex.html",
            {
                "error": "Roll number not found. Please enter a valid roll number.",
            },
        )


def submitted(request):
    return render(request, "StudentView/Submitted.html")

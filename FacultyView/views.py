from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.conf import settings
from .models import Student
import qrcode
import socket
import os
from attendance_state import present


def qrgenerator():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]

    link = f"http://{ip}:8000/student/"

    # Function to generate and display a QR code
    def generate_qr_code(link):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(link)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        # Use absolute path to save QR code
        qr_path = os.path.join(settings.BASE_DIR, 'FacultyView', 'static', 'FacultyView', 'qrcode.png')
        os.makedirs(os.path.dirname(qr_path), exist_ok=True)
        img.save(qr_path)

    generate_qr_code(link)


def faculty_view(request):
    if request.method == "POST":
        student_roll = request.POST["student_id"]
        if student_roll in present:
            present.remove(student_roll)
        return HttpResponseRedirect("/")

    else:
        qrgenerator()
        attendance = []
        for entry in present:
            roll = str(entry)
            try:
                student = Student.objects.get(s_roll=roll)
                attendance.append(
                    {
                        "roll": roll,
                        "name": f"{student.s_fname} {student.s_lname}",
                        "manual": False,
                    }
                )
            except Student.DoesNotExist:
                attendance.append(
                    {
                        "roll": roll,
                        "manual": True,
                    }
                )

        return render(
            request,
            "FacultyView/FacultyViewIndex.html",
            {
                "students": attendance,
            },
        )


def add_manually(request):
    students = Student.objects.all().order_by("s_roll")

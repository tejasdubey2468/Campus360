#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'timetable_project.settings')
django.setup()

from scheduler.models import Department, Teacher, Subject, Class, SubjectAssignment, Classroom

print(f'Departments: {Department.objects.count()}')
print(f'Teachers: {Teacher.objects.count()}')
print(f'Subjects: {Subject.objects.count()}')
print(f'Classes: {Class.objects.count()}')
print(f'SubjectAssignments: {SubjectAssignment.objects.count()}')
print(f'Lecture Classrooms: {Classroom.objects.filter(room_type__in=["lecture", "seminar"]).count()}')
print(f'Lab Classrooms: {Classroom.objects.filter(room_type="lab").count()}')

#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'timetable_project.settings')
django.setup()

from scheduler.models import SubjectAssignment, Subject

assignments = SubjectAssignment.objects.all()
for a in assignments:
    print(f'Assignment: {a.subject.name} (ID: {a.subject.id})')
    print(f'  - Lectures per week: {a.lectures_per_week}')
    print(f'  - Has lab: {a.subject.has_lab_component}')
    print(f'  - Labs per week: {a.subject.labs_per_week}')

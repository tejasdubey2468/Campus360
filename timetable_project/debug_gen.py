#!/usr/bin/env python
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'timetable_project.settings')
django.setup()

from scheduler.models import Timetable, SubjectAssignment
from scheduler.constraints import TimetableGenerator

# Create a test timetable
print("Creating timetable...")
timetable = Timetable.objects.create(
    name='Debug Test',
    academic_year='2024',
    semester='Spring'
)
print(f"Timetable created: {timetable.pk}")
print(f"  start_time: {timetable.start_time}")
print(f"  lecture_duration: {timetable.lecture_duration}")
print(f"  break_after_slot: {timetable.break_after_slot}")

# Get assignments
print("\nGetting assignments...")
assignments = list(SubjectAssignment.objects.select_related('subject', 'student_class', 'teacher'))
print(f"Total assignments: {len(assignments)}")
for a in assignments:
    print(f"  - {a.subject.name} for {a.student_class.name}: {a.lectures_per_week} lectures/week")

# Create generator
print("\nCreating generator...")
generator = TimetableGenerator(timetable)

# Add debug prints to the generator
original_generate_time_slots = generator._generate_time_slots
def debug_generate_time_slots():
    print("  Generating time slots...")
    slots = original_generate_time_slots()
    print(f"  Generated {len(slots)} time slots")
    for i, s in enumerate(slots[:5]):  # Show first 5
        if not s['is_break']:
            print(f"    Slot {i}: Day {s['day']}, {s['start']}-{s['end']}")
    return slots

generator._generate_time_slots = debug_generate_time_slots

# Run generation
print("\nGenerating timetable...")
try:
    result, message = generator.generate()
    print(f"Result: {result}")
    print(f"Message: {message}")
finally:
    # Clean up
    timetable.delete()
    print("\nTimetable cleaned up")

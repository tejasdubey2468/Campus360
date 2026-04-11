from django.core.management.base import BaseCommand
from scheduler.models import (
    Department, Teacher, Classroom, TimeSlot, Class, Subject, 
    SubjectAssignment, TeacherAvailability
)

class Command(BaseCommand):
    help = 'Populate the database with sample data for timetable generation'

    def handle(self, *args, **options):
        self.stdout.write('Populating sample data...')

        # Create departments
        cs = Department.objects.create(name='Computer Science', code='CS')
        math = Department.objects.create(name='Mathematics', code='MATH')

        # Create teachers
        teacher1 = Teacher.objects.create(name='Dr. Smith', email='smith@college.edu', department=cs)
        teacher2 = Teacher.objects.create(name='Prof. Johnson', email='johnson@college.edu', department=cs)
        teacher3 = Teacher.objects.create(name='Dr. Brown', email='brown@college.edu', department=math)

        # Create classrooms
        room1 = Classroom.objects.create(name='CS101', room_type='lecture', capacity=50)
        room2 = Classroom.objects.create(name='CS102', room_type='lecture', capacity=40)
        room3 = Classroom.objects.create(name='Lab1', room_type='lab', capacity=30)
        room4 = Classroom.objects.create(name='Math101', room_type='lecture', capacity=45)

        # Create time slots (Monday to Friday, 9 AM to 5 PM)
        time_slots = []
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        times = [
            ('09:00', '10:00'), ('10:00', '11:00'), ('11:00', '12:00'),
            ('13:00', '14:00'), ('14:00', '15:00'), ('15:00', '16:00'), ('16:00', '17:00')
        ]
        
        for day_idx, day in enumerate(days):
            for start, end in times:
                slot = TimeSlot.objects.create(
                    day=day_idx,
                    start_time=start,
                    end_time=end,
                    is_lab_slot=False
                )
                time_slots.append(slot)
        
        # Add some lab slots (longer duration)
        lab_times = [('09:00', '12:00'), ('13:00', '16:00')]
        for day_idx in [0, 2, 4]:  # Mon, Wed, Fri
            for start, end in lab_times:
                slot = TimeSlot.objects.create(
                    day=day_idx,
                    start_time=start,
                    end_time=end,
                    is_lab_slot=True
                )
                time_slots.append(slot)

        # Create classes
        cs_class = Class.objects.create(
            name='Computer Science 3rd Year', 
            department=cs, 
            year=3, 
            section='A', 
            strength=45
        )
        math_class = Class.objects.create(
            name='Mathematics 2nd Year', 
            department=math, 
            year=2, 
            section='B', 
            strength=40
        )

        # Create subjects
        ds = Subject.objects.create(
            name='Data Structures', 
            code='CS301', 
            subject_type='theory', 
            credits=4, 
            hours_per_week=4,
            lectures_per_week=3,
            has_lab_component=False
        )
        algo = Subject.objects.create(
            name='Algorithms', 
            code='CS302', 
            subject_type='theory', 
            credits=4, 
            hours_per_week=4,
            lectures_per_week=3,
            has_lab_component=False
        )
        lab = Subject.objects.create(
            name='Programming Lab', 
            code='CS303', 
            subject_type='lab', 
            credits=2, 
            hours_per_week=3,
            lectures_per_week=1,
            has_lab_component=True
        )
        calc = Subject.objects.create(
            name='Calculus', 
            code='MATH201', 
            subject_type='theory', 
            credits=4,
            hours_per_week=4,
            lectures_per_week=4,
            has_lab_component=False
        )

        # Create subject assignments
        SubjectAssignment.objects.create(subject=ds, student_class=cs_class, teacher=teacher1, lectures_per_week=3)
        SubjectAssignment.objects.create(subject=algo, student_class=cs_class, teacher=teacher2, lectures_per_week=3)
        SubjectAssignment.objects.create(subject=lab, student_class=cs_class, teacher=teacher1, lectures_per_week=1)
        SubjectAssignment.objects.create(subject=calc, student_class=math_class, teacher=teacher3, lectures_per_week=4)

        # Set teacher availabilities (all slots available by default, but let's make some unavailable)
        # For simplicity, assume all are available

        self.stdout.write(self.style.SUCCESS('Sample data populated successfully!'))
        self.stdout.write(f'Created {len(time_slots)} time slots, {Department.objects.count()} departments, etc.')
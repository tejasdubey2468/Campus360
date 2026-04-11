from django.core.management.base import BaseCommand
from scheduler.models import Timetable
from scheduler.constraints import TimetableGenerator

class Command(BaseCommand):
    help = 'Generate a sample timetable'

    def add_arguments(self, parser):
        parser.add_argument('--name', type=str, default='Sample Timetable', help='Name of the timetable')
        parser.add_argument('--year', type=str, default='2024', help='Academic year')
        parser.add_argument('--semester', type=str, default='Spring', help='Semester')

    def handle(self, *args, **options):
        self.stdout.write('Generating timetable...')

        # Create timetable instance
        timetable = Timetable.objects.create(
            name=options['name'],
            academic_year=options['year'],
            semester=options['semester']
        )

        # Generate using constraint solver
        generator = TimetableGenerator(timetable)
        result, message = generator.generate()

        if result:
            self.stdout.write(self.style.SUCCESS(message))
            self.stdout.write(f'Timetable ID: {timetable.pk}')
        else:
            self.stdout.write(self.style.ERROR(message))
            # Clean up failed timetable
            timetable.delete()
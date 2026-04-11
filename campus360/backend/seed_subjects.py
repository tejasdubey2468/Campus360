import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus360_api.settings')
django.setup()

from students.models import Subject
from accounts.models import Department

def seed_subjects():
    cse = Department.objects.filter(code='CSE').first()
    it = Department.objects.filter(code='IT').first()
    
    if not cse or not it:
        print("Required departments missing (CSE/IT).")
        return

    subjects_data = [
        {"name": "Data Structures", "code": "CS301", "dept": cse, "sem": 3, "credits": 4},
        {"name": "Operating Systems", "code": "CS401", "dept": cse, "sem": 4, "credits": 3},
        {"name": "Java Programming", "code": "IT302", "dept": it, "sem": 3, "credits": 4},
        {"name": "Design Thinking", "code": "CS101", "dept": cse, "sem": 1, "credits": 2},
        {"name": "Microprocessor 8086", "code": "EC405", "dept": cse, "sem": 4, "credits": 4},
    ]

    for data in subjects_data:
        Subject.objects.get_or_create(
            code=data["code"],
            defaults={
                "name": data["name"],
                "department": data["dept"],
                "semester": data["sem"],
                "credits": data["credits"],
                "subject_type": "LECTURE"
            }
        )
    print(f"Seeded {len(subjects_data)} subjects.")

if __name__ == "__main__":
    seed_subjects()

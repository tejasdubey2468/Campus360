import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus360_api.settings')
django.setup()

from gymkhana.models import Equipment, Turf

def seed():
    # Equipment
    equip_items = [
        {"name": "Cricket Kit", "cat": "Cricket", "qty": 10},
        {"name": "Football", "cat": "Football", "qty": 15},
        {"name": "Badminton", "cat": "Badminton", "qty": 20},
        {"name": "Basketball", "cat": "Basketball", "qty": 5},
    ]
    
    for item in equip_items:
        Equipment.objects.get_or_create(
            equipment_name=item["name"],
            defaults={
                "category": item["cat"],
                "quantity": item["qty"],
                "available_quantity": item["qty"]
            }
        )
    
    # Turfs
    turf_items = [
        {"name": "Table Tennis Board", "loc": "Indoor Hall"},
        {"name": "Carrom & Chess", "loc": "Recreation Room"},
        {"name": "Main Campus Gym", "loc": "Gym Wing"},
    ]
    
    for item in turf_items:
        Turf.objects.get_or_create(
            turf_name=item["name"],
            defaults={"location": item["loc"]}
        )

    print("Database seeded successfully with Gymkhana items!")

if __name__ == "__main__":
    seed()

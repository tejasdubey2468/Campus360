from django.db import connection
with connection.cursor() as cursor:
    cursor.execute('ALTER TABLE notifications ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE')
print("Column is_active added to notifications table.")

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flowserve_soft.settings')
django.setup()

from django.db import connection

def check_form_data():
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, form_name, status FROM form_data")
        rows = cursor.fetchall()
        print("Fields in form_data:")
        for row in rows:
            print(f"ID: {row[0]}, Name: {row[1]}, Status: {row[2]}")

if __name__ == "__main__":
    check_form_data()

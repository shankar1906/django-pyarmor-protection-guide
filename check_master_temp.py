import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flowserve_soft.settings')
django.setup()

from django.db import connection

def check_master_temp_data():
    with connection.cursor() as cursor:
        cursor.execute("DESCRIBE master_temp_data")
        rows = cursor.fetchall()
        print("Columns in master_temp_data:")
        for row in rows:
            print(row[0])

if __name__ == "__main__":
    check_master_temp_data()

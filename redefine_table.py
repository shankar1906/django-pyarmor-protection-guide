import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flowserve_soft.settings')
django.setup()

from django.db import connection

def redefine_form_data1():
    with connection.cursor() as cursor:
        # Drop existing table
        cursor.execute("DROP TABLE IF EXISTS form_data1")
        
        # Create new table
        # We'll use 50 columns groups (ID, NAME, TYPE, MANDATORY)
        cols = []
        for i in range(1, 51):
            cols.append(f"COL{i}_ID INT DEFAULT NULL")
            cols.append(f"COL{i}_NAME VARCHAR(255) DEFAULT NULL")
            cols.append(f"COL{i}_TYPE VARCHAR(50) DEFAULT NULL")
            cols.append(f"COL{i}_MANDATORY VARCHAR(10) DEFAULT NULL")
            
        create_query = f"""
            CREATE TABLE form_data1 (
                valve_type_id INT PRIMARY KEY,
                {', '.join(cols)}
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
        """
        cursor.execute(create_query)
        print("Table form_data1 redefined successfully.")

if __name__ == "__main__":
    redefine_form_data1()

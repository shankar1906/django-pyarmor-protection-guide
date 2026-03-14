from django.db import connection

def get_all_form_data():
    """
    Fetch all records from form_data table.
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, form_name, status
            FROM form_data
            ORDER BY status DESC, id
        """)
        return cursor.fetchall()

def check_duplicate_form_name(form_name, form_id=None):
    """
    Check if a form name already exists, excluding the current ID if provided.
    """
    with connection.cursor() as cursor:
        if form_id:
            cursor.execute("""
                SELECT id, form_name FROM form_data 
                WHERE LOWER(form_name) = %s AND id != %s
            """, [form_name.lower(), form_id])
        else:
            cursor.execute("""
                SELECT id, form_name FROM form_data 
                WHERE LOWER(form_name) = %s
            """, [form_name.lower()])
        return cursor.fetchone()

def update_form_data_entry(form_id, form_name, status):
    """
    Insert or update a form data entry.
    If form_id is 0 or None, it will insert a new record.
    """
    with connection.cursor() as cursor:
        if form_id and int(form_id) > 0:
            cursor.execute("""
                UPDATE form_data
                SET form_name = %s, status = %s, updated_at = NOW()
                WHERE id = %s
            """, [form_name, status, form_id])
        else:
            cursor.execute("""
                INSERT INTO form_data (form_name, status)
                VALUES (%s, %s)
            """, [form_name, status])

def delete_form_data_entry(form_id):
    """
    Delete a form data record by ID.
    """
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM form_data WHERE id = %s", [form_id])

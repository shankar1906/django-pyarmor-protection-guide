from django.db import connection

def get_all_form_data2_records():
    """
    Fetch a list of valve types that have field configurations.
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT vt.ID, vt.TYPE_ID, vt.TYPE_NAME 
            FROM valve_type vt
            INNER JOIN form_data1 fd1 ON vt.TYPE_ID = fd1.valve_type_id
            ORDER BY vt.TYPE_NAME
        """)
        rows = cursor.fetchall()
        return [
            {
                'id': r[0], 
                'type_id': r[1], 
                'name': r[2],
                'status': 'Configured'
            } for r in rows
        ]

def get_form_data2_by_valve_type(valve_type_id):
    """
    Fetch all field configurations for a specific valve type from form_data1.
    Unpacks COLx columns into a list of field objects.
    """
    if not valve_type_id:
        return []
        
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM form_data1 WHERE valve_type_id = %s", [valve_type_id])
        row = cursor.fetchone()
        if not row:
            return []
            
        # Get column names to handle indexing correctly
        columns = [col[0] for col in cursor.description]
        col_dict = dict(zip(columns, row))
        
        fields = []
        # Join with form_data to get the names
        cursor.execute("SELECT id, form_name FROM form_data")
        form_data_lookup = {r[0]: r[1] for r in cursor.fetchall()}
        
        for i in range(1, 26):
            f_id = col_dict.get(f'COL{i}_ID')
            if f_id is None:
                continue
                
            fields.append({
                'form_data_id': f_id,
                'form_name': col_dict.get(f'COL{i}_NAME') or form_data_lookup.get(f_id, f"Unknown Field {f_id}"),
                'datatype': col_dict.get(f'COL{i}_TYPE'),
                'mandatory': col_dict.get(f'COL{i}_MANDATORY'),
                'toggle': 1 # It's stored in a COL, so it's implicitly enabled
            })
        return fields

def get_enabled_form_data():
    """
    Fetch all enabled form data entries for the dropdown.
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, form_name 
            FROM form_data 
            WHERE status = 'ENABLE'
            ORDER BY form_name
        """)
        rows = cursor.fetchall()
        return [{'id': row[0], 'name': row[1]} for row in rows]

def save_form_data2(valve_type_id, items, is_update=False):
    """
    Bulk save/update form data 2 items for a valve type in a single row.
    Only enabled items (toggle=1) are stored sequentially.
    """
    if not valve_type_id:
        return {'success': False, 'error': 'Valve Type ID is required.'}
        
    try:
        # Filter only enabled items
        enabled_items = [item for item in items if int(item.get('toggle', 1)) == 1]
        
        # Prepare columns and values
        update_fields = ['valve_type_id = %s']
        update_values = [valve_type_id]
        
        for i in range(1, 26):
            if i <= len(enabled_items):
                item = enabled_items[i-1]
                update_fields.append(f"COL{i}_ID = %s")
                update_fields.append(f"COL{i}_NAME = %s")
                update_fields.append(f"COL{i}_TYPE = %s")
                update_fields.append(f"COL{i}_MANDATORY = %s")
                update_values.append(item.get('form_data_id'))
                update_values.append(item.get('form_name'))
                update_values.append(item.get('datatype'))
                update_values.append(item.get('mandatory', 'no'))
            else:
                # Clear remaining columns by setting to NULL via None
                update_fields.append(f"COL{i}_ID = %s")
                update_fields.append(f"COL{i}_NAME = %s")
                update_fields.append(f"COL{i}_TYPE = %s")
                update_fields.append(f"COL{i}_MANDATORY = %s")
                update_values.append(None)
                update_values.append(None)
                update_values.append(None)
                update_values.append(None)
        
        with connection.cursor() as cursor:
            # Check if record exists
            cursor.execute("SELECT COUNT(*) FROM form_data1 WHERE valve_type_id = %s", [valve_type_id])
            exists = cursor.fetchone()[0] > 0
            
            if not is_update and exists:
                return {'success': False, 'error': 'This Valve Type is already configured. Please use Edit instead.'}
            
            if exists:
                query = f"UPDATE form_data1 SET {', '.join(update_fields[1:])} WHERE valve_type_id = %s"
                cursor.execute(query, update_values[1:] + [valve_type_id])
            else:
                field_names = ['valve_type_id'] + [f.split(' = ')[0] for f in update_fields[1:]]
                placeholders = ['%s'] * len(field_names)
                query = f"INSERT INTO form_data1 ({', '.join(field_names)}) VALUES ({', '.join(placeholders)})"
                cursor.execute(query, update_values)
            
            return {'success': True, 'message': 'Form Data 2 saved successfully!'}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}

def bulk_delete_form_data2_by_valve_types(valve_type_ids):
    """
    Delete all field configurations for the specified valve type IDs.
    """
    if not valve_type_ids:
        return {'success': False, 'error': 'No Valve Type IDs provided'}
        
    try:
        with connection.cursor() as cursor:
            placeholder = ', '.join(['%s'] * len(valve_type_ids))
            cursor.execute(f"DELETE FROM form_data1 WHERE valve_type_id IN ({placeholder})", valve_type_ids)
            return {'success': True, 'message': f'Deleted configurations for {len(valve_type_ids)} valve types.'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def delete_form_data2_for_valve_type(valve_type_id):
    """
    Delete all field configurations for a specific valve type.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM form_data1 WHERE valve_type_id = %s", [valve_type_id])
            return {'success': True, 'message': 'Valve type configurations removed successfully!'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


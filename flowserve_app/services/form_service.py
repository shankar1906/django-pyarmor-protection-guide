from django.db import connection

def get_valve_standard():
    with connection.cursor() as cursor:
        cursor.execute("SELECT STANDARD_NAME FROM standard")
        return [row[0] for row in cursor.fetchall()]
    
def get_valve_size():
    with connection.cursor() as cursor:
        cursor.execute("SELECT SIZE_NAME FROM valvesize")
        return [row[0] for row in cursor.fetchall()]

def get_valve_class():
    with connection.cursor() as cursor:
        cursor.execute("SELECT CLASS_NAME FROM valveclass")
        return [row[0] for row in cursor.fetchall()]

def get_shell_material():
    with connection.cursor() as cursor:
        cursor.execute("SELECT SHELL_MATERIAL_NAME FROM shell_material")
        return [row[0] for row in cursor.fetchall()]
    
def get_valve_type():
    with connection.cursor() as cursor:
        cursor.execute("SELECT TYPE_ID, TYPE_NAME FROM valve_type")
        return [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]
    
def get_testername():
    """Get all employee names (kept for backward compatibility)"""
    print("Fetching tester names from database...")
    with connection.cursor() as cursor:
        cursor.execute("select name from employee where superuser=%s ",[0])
        return [row[0] for row in cursor.fetchall()]

def get_assemblers():
    """Get employees with type 'Approver' for Assembled By dropdown"""
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM employee WHERE superuser=%s AND LOWER(employee_type)=%s AND status=%s ORDER BY name", [0, 'approver','active'])
        return [row[0] for row in cursor.fetchall()]

def get_testers():
    """Get employees with type 'Tester' for Tested By dropdown"""
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM employee WHERE superuser=%s AND LOWER(employee_type)=%s AND status=%s ORDER BY name", [0, 'tester','active'])
        return [row[0] for row in cursor.fetchall()]


def get_testname(standard, valve_size, valve_type, shell_material, valve_class):
    with connection.cursor() as cursor:
        
        cursor.execute("SELECT STANDARD_ID FROM standard WHERE STANDARD_NAME=%s", [standard])
        standard_id = cursor.fetchone()[0]

        cursor.execute("SELECT SIZE_ID FROM valvesize WHERE SIZE_NAME=%s", [valve_size])
        size_id = cursor.fetchone()[0]

        cursor.execute("SELECT TYPE_ID FROM valve_type WHERE TYPE_NAME=%s", [valve_type])
        type_id = cursor.fetchone()[0]

        cursor.execute("SELECT TEST_ID FROM valvetype_testtype WHERE TYPE_ID=%s", [type_id])
        test_ids = cursor.fetchall()

        cursor.execute("SELECT SHELL_MATERIAL_ID FROM shell_material WHERE SHELL_MATERIAL_NAME=%s", [shell_material])
        shell_material_id = cursor.fetchone()[0]

        cursor.execute("SELECT CLASS_ID FROM valveclass WHERE CLASS_NAME=%s", [valve_class])
        class_id = cursor.fetchone()[0]

        # test names
        test_name = []
        for t in test_ids:
            cursor.execute("SELECT test_name FROM test_type WHERE test_id=%s", [t[0]])
            test_name.append(cursor.fetchone()[0])
        
        if not test_ids:
             raise ValueError(f"No tests found for Valve Type '{valve_type}'.")

        # pressure columns
        pressure = []
        duration = []

        for t in test_ids:
            cursor.execute("SELECT pre_col_name FROM test_type WHERE test_id=%s", [t[0]])
            pressure_rows = cursor.fetchall()

            for r in pressure_rows:
                pre_col = r[0]
                query = f"SELECT {pre_col} FROM master_pressure_data WHERE SHELLMATERIAL_ID=%s AND VALVECLASS_ID=%s"
                cursor.execute(query, [shell_material_id, class_id])
                row = cursor.fetchone()
                if not row:
                     raise ValueError(f"Combination of Body Material '{shell_material}' and Class '{valve_class}' not found in Pressure data.")
                pressure.append(row[0] if row else None)

            cursor.execute("SELECT dur_col_name FROM test_type WHERE test_id=%s", [t[0]])
            duration_rows = cursor.fetchall()

            for d in duration_rows:
                dur_col = d[0]
                query = f"SELECT {dur_col} FROM master_duration_data WHERE SIZE_ID=%s AND STANDARD_ID=%s"
                cursor.execute(query, [size_id, standard_id])
                row1 = cursor.fetchone()
                if not row1:
                    raise ValueError(f"Combination of Size '{valve_size}' and Standard '{standard}' not found in Duration data.")
                duration.append(row1[0] if row1 else None)

        return test_name, pressure, duration, test_ids


# ==================== STATION SERVICES ====================

def get_status():
    """Get status for station 1"""
    with connection.cursor() as cursor:
        # Fetch statuses
        cursor.execute("SELECT STATION_STATUS FROM master_temp_data WHERE id=1")
        row = cursor.fetchone()
        
        return row[0] if row else "Disabled"

def get_station_data():
    """Get data for station 1"""
    with connection.cursor() as cursor:
        try:
            # First check if record exists
            cursor.execute("SELECT COUNT(*) FROM master_temp_data WHERE id=1")
            count = cursor.fetchone()[0]
            
            if count == 0:
                # Create default record if it doesn't exist
                cursor.execute("""
                    INSERT INTO master_temp_data (id, CLASS_NAME, SIZE_NAME, SHELL_MATERIAL_NAME, TYPE_NAME, PRESSURE_UNIT, STATION_STATUS, CYCLE_COMPLETE)
                    VALUES (1, NULL, NULL, NULL, NULL, NULL, 'Disabled', 'No')
                """)
                print("Created default record in master_temp_data for ID=1")
            
            cursor.execute("""
                SELECT CLASS_NAME, SIZE_NAME, SHELL_MATERIAL_NAME, TYPE_NAME, PRESSURE_UNIT 
                FROM master_temp_data WHERE id=1
            """)
            station1_data = cursor.fetchone()
            
            # Log the data for debugging
            if station1_data:
                print(f"Station data retrieved: {station1_data}")
            else:
                print("No station data found for ID=1")
                
            return station1_data
        except Exception as e:
            print(f"Error in get_station_data: {e}")
            return None

def cancel_station1():
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM temp_testing_data_s1")
        # Reset main fields
        cursor.execute("""
            UPDATE master_temp_data 
            SET STATION_STATUS='Disabled', CYCLE_COMPLETE='No', 
                VALVE_SER_NO='', PRESSURE_UNIT='', STANDARD_NAME='', 
                SIZE_NAME='', CLASS_NAME='', TYPE_NAME='', 
                SHELL_MATERIAL_NAME=''
            WHERE ID=1
        """)
        # Reset all COLx columns (up to 50 based on DB description)
        column_updates = []
        for i in range(1, 51):
            column_updates.append(f"COL{i}_NAME=''")
            column_updates.append(f"COL{i}_VALUE=''")
        
        set_clause = ", ".join(column_updates)
        cursor.execute(f"UPDATE master_temp_data SET {set_clause} WHERE ID=1")

def clear_station1():
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM temp_testing_data_s1")
        cursor.execute("""
            UPDATE master_temp_data 
            SET STATION_STATUS='Disabled', CYCLE_COMPLETE='No',
                VALVE_SER_NO='', PRESSURE_UNIT='', STANDARD_NAME='', 
                SIZE_NAME='', CLASS_NAME='', TYPE_NAME='', 
                SHELL_MATERIAL_NAME=''
            WHERE ID=1
        """)
        column_updates = []
        for i in range(1, 51):
            column_updates.append(f"COL{i}_NAME=''")
            column_updates.append(f"COL{i}_VALUE=''")
        
        set_clause = ", ".join(column_updates)
        cursor.execute(f"UPDATE master_temp_data SET {set_clause} WHERE ID=1")


def get_active_test_ids():
    """Get active test IDs from temp_testing_data_s1"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT TEST_ID 
            FROM temp_testing_data_s1 
            ORDER BY TEST_ID
        """)
        active_tests = cursor.fetchall()
        # Return list of test IDs
        return [test_id for (test_id,) in active_tests]

    

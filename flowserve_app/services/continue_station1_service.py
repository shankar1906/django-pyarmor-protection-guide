from django.db import connection
from flowserve_app.views.api.configuration_api_views import TestleadSmartsyncx

def get_status():
    with connection.cursor() as cursor:
        # Fetch status for station 1
        cursor.execute("SELECT STATION_STATUS FROM master_temp_data WHERE id=1")
        station1_status = cursor.fetchone()[0].lower()
        
        try:
            sync_status = TestleadSmartsyncx.read_holding_registers(2018,1).registers[0]
        except Exception as e:
            print(f"Warning: Could not read sync_status from Modbus: {e}")
            sync_status = 0
        
        return station1_status, sync_status

def get_station_data():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT CLASS_NAME, SIZE_NAME, SHELL_MATERIAL_NAME, TYPE_NAME, PRESSURE_UNIT 
            FROM master_temp_data WHERE id=1
        """)
        station1_data = cursor.fetchone()
        
        return station1_data

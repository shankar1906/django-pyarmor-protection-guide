import os
import django
import json
from django.test import RequestFactory
from django.http import JsonResponse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flowserve_soft.settings')
django.setup()

from flowserve_app.views.api.save_station1_form_api_views import save_station1_form
from django.db import connection

def verify_save():
    factory = RequestFactory()
    
    # Mock data
    payload = {
        "fields": [
            {"name": "Customer", "value": "Test Customer"},
            {"name": "Report No", "value": "REP-001"},
            {"name": "size_s1", "value": "2\""},
            {"name": "class_s1", "value": "150"},
            {"name": "pressureunit_s1", "value": "PSI"},
            {"name": "VALVE SERIAL NO", "value": "SERIAL-12345"},
            {"name": "Tag No", "value": "TAG-X"}
        ],
        "test_mode": "Manual",
        "open_degree_s1": 90,
        "close_degree_s1": 0,
        "testname": ["Shell Test"],
        "test_pressure": [10.5],
        "test_duration": [60],
        "test_id": [[1]],
        "diabled_testid": []
    }
    
    request = factory.post('/api/newform/save_station1/', 
                           data=json.dumps(payload), 
                           content_type='application/json')
    
    # We might need to mock TestleadSmartsyncx and getstatus if they depend on hardware
    # For now, let's see if it runs. If it fails on Modbus, we'll know.
    
    print("Executing save_station1_form...")
    try:
        response = save_station1_form(request)
        print(f"Response: {response.content}")
        
        if response.status_code == 200:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM master_temp_data WHERE ID = 1")
                row = cursor.fetchone()
                columns = [col[0] for col in cursor.description]
                data = dict(zip(columns, row))
                
                print("\nVerification Results:")
                print(f"COL1_NAME: {data.get('COL1_NAME')} | COL1_VALUE: {data.get('COL1_VALUE')}")
                print(f"COL2_NAME: {data.get('COL2_NAME')} | COL2_VALUE: {data.get('COL2_VALUE')}")
                print(f"COL3_NAME: {data.get('COL3_NAME')} | COL3_VALUE: {data.get('COL3_VALUE')}")
                print(f"VALVE_SER_NO: {data.get('VALVE_SER_NO')}")
                print(f"SIZE_NAME: {data.get('SIZE_NAME')}")
                
                # Check expectations
                assert data.get('COL1_NAME') == "Customer"
                assert data.get('COL1_VALUE') == "Test Customer"
                assert data.get('VALVE_SER_NO') == "SERIAL-12345"
                print("\nSUCCESS: Data verified in master_temp_data")
        else:
            print(f"FAILED: Status code {response.status_code}")
            
    except Exception as e:
        print(f"Error during verification: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_save()

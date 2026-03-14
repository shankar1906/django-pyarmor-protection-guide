from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from flowserve_app.services.save_station1_service import (
    save_station1, insert_pressure_duration,
    check_duplicate_serial_station1, check_hmi_connection
)
from flowserve_app.views.api.configuration_api_views import TestleadSmartsyncx
from flowserve_app.views.api.single_live_page_api_views import getstatus
from flowserve_app.src import HmiAddress
from django.db import connection

@csrf_exempt
def save_station1_form(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=400)

    try:
        # Check HMI connection status before saving
        if not check_hmi_connection():
            return JsonResponse({
                "status": "error",
                "message": "HMI is not connected. Please connect HMI before saving the form."
            }, status=400)
        
        data = json.loads(request.body.decode("utf-8"))
    
        fields = data.get("fields", [])
        field_dict = {item.get("name"): item.get("value") for item in fields}
        pressureunit = field_dict.get("pressureunit_s1")
        
        
        station_status = "Enabled"
        cycle_complete = "No"
        testname = data.get("testname")
        test_pressure = data.get("test_pressure")
        test_duration = data.get("test_duration")
        active_testid = data.get("test_id")
        diabled_testid = data.get("diabled_testid")
        open_degree_s1 = data.get("open_degree_s1")
        close_degree_s1 = data.get("close_degree_s1")
        testmode = data.get("test_mode")

        print('open_degree_s1',open_degree_s1)
        
        # Check if at least one test is active (enabled)
        if not active_testid or len(active_testid) == 0:
            return JsonResponse({
                "status": "error",
                "message": "Please enable at least one test to proceed. Cannot save form without any active tests."
            }, status=400)
        
        # Check if all tests are disabled
        if diabled_testid and len(diabled_testid) >= len(active_testid):
            return JsonResponse({
                "status": "error",
                "message": "Please enable at least one test to proceed. All tests are currently disabled."
            }, status=400)
        
        # Write to Modbus registers
        try:
            print("printing")
            # Write degree values to correct addresses
            TestleadSmartsyncx.write_register(HmiAddress.SET_OPEN_DEGREE, open_degree_s1)
            TestleadSmartsyncx.write_register(HmiAddress.SET_CLOSE_DEGREE, close_degree_s1)
            
            # Read current torque values and write them to ensure they are set
            current_open_torque = getstatus(HmiAddress.SET_OPEN_TORQUE)
            current_close_torque = getstatus(HmiAddress.SET_CLOSE_TORQUE)
            if current_open_torque is not None:
                TestleadSmartsyncx.write_register(HmiAddress.SET_OPEN_TORQUE, current_open_torque)
            if current_close_torque is not None:
                TestleadSmartsyncx.write_register(HmiAddress.SET_CLOSE_TORQUE, current_close_torque)
        except Exception as e:
            print(f"Error writing to Modbus: {e}")
          
        
        if not fields:
            return JsonResponse({"error": "No fields found"}, status=400)

        # Convert list → dictionary
        field_dict = {item["name"]: item["value"] for item in fields}

        # Prepare dynamic fields for COLx_NAME and COLx_VALUE
        update_fields = []
        update_values = []

        # List of fixed fields to exclude from COL mapping
        excluded_fields = [
            "size_s1", "class_s1", "pressureunit_s1", "standard_s1", 
            "type_s1", "body_material_s1", "VALVE_SER_NO", "VALVE SERIAL NO"
        ]

        index = 1
        for key, value in field_dict.items():
            if key in excluded_fields:
                continue

            if index > 23:
                break  # limit to COL1–COL23 to avoid overwriting torque data

            update_fields.append(f"COL{index}_NAME = %s")
            update_fields.append(f"COL{index}_VALUE = %s")
            update_values.append(key)     # name
            update_values.append(value)   # value
            index += 1
            
        # Blank out remaining columns so old values don't linger
        for i in range(index, 24):
            update_fields.append(f"COL{i}_NAME = %s")
            update_fields.append(f"COL{i}_VALUE = %s")
            update_values.append("")
            update_values.append("")

        # Add final fixed fields
        update_fields += [
            "SIZE_NAME = %s",
            "CLASS_NAME = %s",
            "PRESSURE_UNIT = %s",
            "STANDARD_NAME = %s",
            "TYPE_NAME = %s",
            "SHELL_MATERIAL_NAME = %s",
            "VALVE_SER_NO = %s",
            "STATION_STATUS = %s",
            "CYCLE_COMPLETE = %s"
        ]

        # Handle VALVE SERIAL NO vs VALVE_SER_NO naming
        valve_serial = field_dict.get("VALVE_SER_NO") or field_dict.get("VALVE SERIAL NO")

        update_values += [
            field_dict.get("size_s1"),
            field_dict.get("class_s1"),
            field_dict.get("pressureunit_s1"),
            field_dict.get("standard_s1"),
            field_dict.get("type_s1"),
            field_dict.get("body_material_s1"),
            valve_serial,
            station_status,
            cycle_complete
        ]

        # Add WHERE ID
        update_values.append(1)

        # Build final update query
        query = f"""
            UPDATE master_temp_data
            SET {', '.join(update_fields)}
            WHERE ID = %s
        """

        save_station1(query,update_values)
        
        valve_serial_no = valve_serial
        insert_pressure_duration(testname,test_pressure,test_duration,active_testid,diabled_testid,pressureunit,valve_serial_no)
        return JsonResponse({"status": "success", "message": "Updated master_temp_data successfully"})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)

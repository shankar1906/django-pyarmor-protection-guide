from django.http import JsonResponse
from flowserve_app.services.form_service import get_status, get_station_data, get_testname, get_active_test_ids
import traceback
from flowserve_app.src import HmiAddress
from flowserve_app.views.api.configuration_api_views import TestleadSmartsyncx

   
def write_to_hmi(place, value):
    try:
        TestleadSmartsyncx.write_register(place, value)
        return True
    except Exception as e:
        print(f"[Error writing to HMI] {e}")
        return False

def continue_station1(request):
    try:
        # Get status from service (only station1 now)
        station1_status = get_status()
        
        # Default redirect
        redirect_url = "/single_page/"

        print(f"DEBUG continue_station1: raw get_status() result is {repr(station1_status)}")

        # ---- Logic ----
        # Since we only have station1, always redirect to single_page if enabled
        if station1_status and str(station1_status).strip().lower() == "enabled":
            redirect_url = "/single_page/"
            
            # Get station data to write degree values to HMI
            try:
                station_data = get_station_data()
                if station_data and all(field is not None for field in station_data):
                    class_name, size_name, shell_material_name, type_name, pressure_unit = station_data
                    
                    if size_name and type_name:
                        # Get degree values from database and write to HMI
                        from django.db import connection
                        with connection.cursor() as cursor:
                            # Get SIZE_ID and TYPE_ID
                            cursor.execute("SELECT SIZE_ID FROM valvesize WHERE SIZE_NAME = %s", [size_name])
                            size_result = cursor.fetchone()
                            cursor.execute("SELECT TYPE_ID FROM valve_type WHERE TYPE_NAME = %s", [type_name])
                            type_result = cursor.fetchone()
                            
                            if size_result and type_result:
                                size_id = size_result[0]
                                type_id = type_result[0]
                                
                                # Get degree values
                                cursor.execute("SELECT OPEN_DEGREE, CLOSE_DEGREE FROM master_degree_data WHERE SIZE_ID = %s AND TYPE_ID = %s", [size_id, type_id])
                                degree_result = cursor.fetchone()
                                
                                if degree_result:
                                    open_degree, close_degree = degree_result
                                    # Write degree values to HMI
                                    write_to_hmi(HmiAddress.SET_OPEN_DEGREE, open_degree)
                                    write_to_hmi(HmiAddress.SET_CLOSE_DEGREE, close_degree)
                                    print(f"Written degree values to HMI: Open={open_degree}, Close={close_degree}")
                else:
                    print("Station data is None or contains null values - skipping degree write to HMI")
                                    
            except Exception as degree_error:
                print(f"Error writing degree values to HMI: {degree_error}")
                print(f"Station data was: {station_data}")
                # Continue with redirect even if degree write fails
            
            # Get active test IDs using service
            try:
                active_test_ids = get_active_test_ids()
                
                if active_test_ids:
                    print(f"Found {len(active_test_ids)} active tests: {active_test_ids}")
                    
                    # Map test IDs to HMI addresses
                    test_to_address = {
                        1: 2025,
                        2: 2026,
                        3: 2027,
                        4: 2028,
                        5: 2029
                    }
                    
                    # Write active test status to corresponding HMI addresses
                    for test_id in active_test_ids:
                        if test_id in test_to_address:
                            address = test_to_address[test_id]
                            success = write_to_hmi(address, 1)
                        else:
                            print(f"Warning: Test ID {test_id} has no corresponding HMI address")
                else:
                    print("No active tests found in temp_testing_data_s1")
                    
            except Exception as service_error:
                print(f"Service error while getting active tests: {service_error}")
                # Continue with redirect even if HMI write fails
            
        else:
            return JsonResponse({
                "status": "failure",
                "message": "Station 1 is not enabled."
            })

        # Final consistent return
        return JsonResponse({
            "status": "success",
            "redirect_url": redirect_url,
            "station1_status": station1_status
        })

    except Exception as e:
        print("Error in continue_station1:", e)
        print(traceback.format_exc())
        return JsonResponse({
            "status": "failure",
            "message": f"Error: {str(e)}"
        })

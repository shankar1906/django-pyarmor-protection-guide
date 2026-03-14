from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from flowserve_app.decorators import permission_required
import json
from flowserve_app.services.form_service import get_testname
from flowserve_app.services.gauge_details_service import get_valid_gauges_for_station
    
# @csrf_exempt
# @permission_required("form")
# def get_pressure_duration(request):
#     if request.method == "POST":
#         data = json.loads(request.body)
#         standard = data.get("standard")
#         valve_size = data.get("size")
#         valve_class = data.get("class")
#         valve_type = data.get("type")
#         shell_material = data.get("body_material")
#         pressure_unit = data.get("pressure_unit")
#         station = data.get("station")
        
#         test_name, pressure, duration,test_ids,degree = get_testname(
#             standard, valve_size, valve_type, shell_material, valve_class
#         )
        
#         if pressure_unit.lower() == "psi":
#             pressure = [float(p) * 14.5 for p in pressure]
            
#         pressure_duration = {
#             "test_name": test_name,
#             "pressure": pressure,
#             "duration": duration,
#             "testid":test_ids,
#             "degree":degree
#         }
#         return JsonResponse({"pressure_duration": pressure_duration})
    


@csrf_exempt
@permission_required("form")
def get_pressure_duration(request):
    try:
        if request.method == "POST":
            data = json.loads(request.body)
            standard = data.get("standard")
            valve_size = data.get("size")
            valve_class = data.get("class")
            valve_type = data.get("type")
            shell_material = data.get("body_material")
            pressure_unit = data.get("pressure_unit")
            station = data.get("station")
            
            test_name, pressure, duration, test_ids = get_testname(
                standard, valve_size, valve_type, shell_material, valve_class
            )
            
            # Database stores pressure in PSI
            # If BAR is selected, convert from PSI to BAR by dividing by 14.5
            if pressure_unit.lower() == "bar":
                pressure = [float(p) / 14.5 for p in pressure]
                invalid = [p for p in pressure if p is None]

                if invalid:
                    raise ValueError("Pressure contains NULL values. Check test configuration.")

            # Get enabled and valid gauges
            st_id = 1
            if station and station.lower().startswith("station"):
                st_id_str = station.lower().replace("station", "")
                if st_id_str.isdigit():
                    st_id = int(st_id_str)
            
            raw_gauges = get_valid_gauges_for_station(st_id)
            gauges = []
            for g in raw_gauges:
                done_date = g[1]
                due_date = g[2]
                if hasattr(done_date, 'strftime'):
                    done_date = done_date.strftime('%Y-%m-%d')
                if hasattr(due_date, 'strftime'):
                    due_date = due_date.strftime('%Y-%m-%d')
                    
                gauges.append({
                    "instrument_type": g[0], 
                    "cal_done_date": str(done_date) if done_date else "", 
                    "cal_due_date": str(due_date) if due_date else ""
                })

            pressure_duration = {
                "test_name": test_name,
                "pressure": pressure,
                "duration": duration,
                "testid": test_ids,
                "gauges": gauges
            }
            return JsonResponse({"pressure_duration": pressure_duration})

    except TypeError as e:
        return JsonResponse({
            "error": "Invalid pressure value (NULL found).",
            "details": str(e)
        }, status=400)

    except ValueError as e:
        return JsonResponse({
            "error": str(e)
        }, status=400)

    except Exception as e:
        return JsonResponse({
            "error": "Unexpected server error",
            "details": str(e)
        }, status=500)

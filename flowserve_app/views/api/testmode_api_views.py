from django.http import JsonResponse
from django.db import connection, transaction, IntegrityError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from flowserve_app.services.dashboard_testmode_service import testmode, check_cyclecomplete

import json


def set_test_mode(request):
    mode = request.GET.get('mode', 'manual')
    testmode(mode)
    return JsonResponse({"status": "success", "mode": mode})


# api
def check_incompletetest(request):
    data = check_cyclecomplete()
    print("incompelte data",  data)

    return JsonResponse({
        "found": bool(data),
        "tests": data,
        "no_of_stations": len(data)
    })




@csrf_exempt
def delete_incomplete_test(request, serialNo, stationNum):

    print("received parameters", stationNum, serialNo )

    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        stationNum = int(stationNum)

        if stationNum not in [1, 2]:
            return JsonResponse({"error": "Invalid station"})

        if stationNum == 1:
            data =  delete_incomplete_test_station1(request, serialNo)

        else:
            data = delete_incomplete_test_station2(request, serialNo)

        return JsonResponse({
            "success": True,   
            "status": "",
            "station":stationNum,
            "data": data
        })
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)




def delete_incomplete_test_station1(request, v_serial_no):  

        with transaction.atomic():
            with connection.cursor() as cursor:

                cursor.execute(f""" 
                    UPDATE master_temp_data
                    SET STATION_STATUS = %s
                    where VALVE_SER_NO = %s 
                """, ["Disabled", v_serial_no])

                cursor.execute(""" TRUNCATE temp_testing_data_s1 """)

                cursor.execute(f"""       
                    DELETE FROM temp_pressure_analysis
                    WHERE VALVE_SER_NO = %s AND 
                    CYCLE_COMPLETE = "No"
                    """,
                    [v_serial_no]
                )

                cursor.execute(f"""       
                    DELETE FROM pressure_analysis
                    WHERE VALVE_SER_NO = %s AND
                    CYCLE_COMPLETE = "No"
                    """,
                    [v_serial_no]
                )

                cursor.execute(""" TRUNCATE current_status_station1 """)
    
        return {
        "valve_serial_no": v_serial_no,
        "station": 1,
        "station_status": "Disabled",
        "deleted": True
        }



def delete_incomplete_test_station2(request, v_serial_no):  

            with transaction.atomic():
                with connection.cursor() as cursor:

                    cursor.execute(f"""
                        UPDATE master_temp_data
                        SET STATION_STATUS = "Disabled"
                        where VALVE_SER_NO = %s 
                    """, [v_serial_no])

                    # cursor.execute(f"""       
                    #     DELETE FROM temp_testing_data_s2
                    #     WHERE VALVE_SERIAL_NO = %s
                    #     """,
                    #     [v_serial_no]
                    # )

                    cursor.execute(""" TRUNCATE temp_testing_data_s2 """)

                    cursor.execute(f"""       
                        DELETE FROM temp_pressure_analysis
                        WHERE VALVE_SER_NO = %s AND
                        CYCLE_COMPLETE = "No"
                        """,
                        [v_serial_no]
                    )
                    cursor.execute(f"""       
                        DELETE FROM pressure_analysis
                        WHERE VALVE_SER_NO = %s AND
                        CYCLE_COMPLETE = "No"
                        """,
                        [v_serial_no]
                    )
                    # cursor.execute(f"""       
                    #     DELETE FROM current_status_station2
                    #     WHERE VALVE_SERIAL_NO = %s
                    #     """,
                    #     [v_serial_no]
                    # )
                    cursor.execute(""" TRUNCATE current_status_station2 """)
    
            return {
                "valve_serial_no": v_serial_no,
                "station": 2,
                "station_status": "Disabled",
                "deleted": True
            }

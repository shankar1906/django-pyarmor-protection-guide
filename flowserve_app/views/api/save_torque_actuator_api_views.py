import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection


@csrf_exempt
def save_torque_actuator_data(request, stationNum, valveSerial):
    """
    Saves Torque & Actuator modal form data into pressure_analysis (COL24-COL39)
    and updates / inserts serial_tbl usage count for the given valve serial.
    """
    if request.method != "POST":
        return JsonResponse({"status": "failure", "message": "Invalid method"}, status=405)

    try:
        body = json.loads(request.body)

        # -----------------------------------------------------------
        # Extract every individual field from the modal form
        # -----------------------------------------------------------
        breakaway_thrust        = body.get("breakaway_thrust", "")
        torque_break_nm         = body.get("torque_break_nm", "")
        torque_run              = body.get("torque_run", "")
        actuator_make           = body.get("actuator_make", "")
        actuator_model          = body.get("actuator_model", "")
        rpm_value               = body.get("rpm_value", "")
        act_s_no                = body.get("act_s_no", "")

        # Opening Torque (2 sub-fields)
        opening_full_torque         = body.get("opening_full_torque", "")          # Open torque % of Full Torque
        opening_torque_act_setting  = body.get("opening_torque_act_setting", "")   # Act setting for Open (Limit Setting)

        # Closing Torque (2 sub-fields)
        closing_full_torque         = body.get("closing_full_torque", "")          # Close torque % of Full Torque
        closing_torque_act_setting  = body.get("closing_torque_act_setting", "")   # Act setting for Close (Limit Setting)

        # Operating Time (3 sub-fields)
        operating_time_gad              = body.get("operating_time_gad", "")               # As Per GAD / Production order
        operating_time_open_to_close    = body.get("operating_time_open_to_close", "")     # Measured Time (Sec) Open to Close
        operating_time_close_to_open    = body.get("operating_time_close_to_open", "")     # Measured Time (Sec) Close to Open

        # Bottom selects
        media_drained       = body.get("media_drained", "")
        bleeder_tightened   = body.get("bleeder_tightened", "")

        # Gauge selects
        hydro_gauge_1       = body.get("hydro_gauge_1", "")
        hydro_gauge_2       = body.get("hydro_gauge_2", "")
        air_gauge_1         = body.get("air_gauge_1", "")
        air_gauge_2         = body.get("air_gauge_2", "")
        hydro_transducer    = body.get("hydro_transducer", "")
        air_transducer      = body.get("air_transducer", "")

        # -----------------------------------------------------------
        # COL24–COL45 name/value pairs (one field per pair)
        # -----------------------------------------------------------
        col_updates = """
                COL24_NAME = %s,  COL24_VALUE = %s,
                COL25_NAME = %s,  COL25_VALUE = %s,
                COL26_NAME = %s,  COL26_VALUE = %s,
                COL27_NAME = %s,  COL27_VALUE = %s,
                COL28_NAME = %s,  COL28_VALUE = %s,
                COL29_NAME = %s,  COL29_VALUE = %s,
                COL30_NAME = %s,  COL30_VALUE = %s,
                COL31_NAME = %s,  COL31_VALUE = %s,
                COL32_NAME = %s,  COL32_VALUE = %s,
                COL33_NAME = %s,  COL33_VALUE = %s,
                COL34_NAME = %s,  COL34_VALUE = %s,
                COL35_NAME = %s,  COL35_VALUE = %s,
                COL36_NAME = %s,  COL36_VALUE = %s,
                COL37_NAME = %s,  COL37_VALUE = %s,
                COL38_NAME = %s,  COL38_VALUE = %s,
                COL39_NAME = %s,  COL39_VALUE = %s,
                COL40_NAME = %s,  COL40_VALUE = %s,
                COL41_NAME = %s,  COL41_VALUE = %s,
                COL42_NAME = %s,  COL42_VALUE = %s,
                COL43_NAME = %s,  COL43_VALUE = %s,
                COL44_NAME = %s,  COL44_VALUE = %s,
                COL45_NAME = %s,  COL45_VALUE = %s
        """

        col_params = [
            "Breakaway_Thrust",                 breakaway_thrust,
            "Torque_Break_Nm",                  torque_break_nm,
            "Torque_Run",                       torque_run,
            "Actuator_Make",                    actuator_make,
            "Actuator_Model",                   actuator_model,
            "RPM_Value",                        rpm_value,
            "Act_S_No",                         act_s_no,
            "Opening_Full_Torque",              opening_full_torque,
            "Opening_Torque_Act_Setting",       opening_torque_act_setting,
            "Closing_Full_Torque",              closing_full_torque,
            "Closing_Torque_Act_Setting",       closing_torque_act_setting,
            "Operating_Time_GAD",               operating_time_gad,
            "Operating_Time_Open_To_Close",     operating_time_open_to_close,
            "Operating_Time_Close_To_Open",     operating_time_close_to_open,
            "Media_Drained",                    media_drained,
            "Bleeder_Tightened",                bleeder_tightened,
            "Hydro_Gauge_1",                    hydro_gauge_1,
            "Hydro_Gauge_2",                    hydro_gauge_2,
            "Air_Gauge_1",                      air_gauge_1,
            "Air_Gauge_2",                      air_gauge_2,
            "Hydro_Transducer",                 hydro_transducer,
            "Air_Transducer",                   air_transducer,
        ]

        with connection.cursor() as cursor:
            # ---- 1. Fetch current Count_No from serial_tbl ----
            cursor.execute("SELECT Count_No FROM serial_tbl WHERE Serial_No = %s", [valveSerial])
            serial_row = cursor.fetchone()
            serial_count = serial_row[0] if serial_row else 1
            print(f"[TORQUE_ACTUATOR] Using COUNT_ID = {serial_count} for {valveSerial}")

            # ---- 2. Update master_temp_data (Always update master session record) ----
            # master_temp_data might also have COUNT_ID? We'll update it if we find it commonly used.
            # For now, following user request strictly for analysis tables.
            cursor.execute(
                f"UPDATE master_temp_data SET {col_updates} WHERE ID = 1",
                col_params
            )
            mtd_rows = cursor.rowcount
            print(f"[TORQUE_ACTUATOR] Updated {mtd_rows} rows in master_temp_data")

            # ---- 3. Process analysis tables ----
            tables = ["temp_pressure_analysis", "pressure_analysis"]
            pa_rows = 0
            tpa_rows = 0

            for table in tables:
                # Check if an active record (CYCLE_COMPLETE='No') exists
                cursor.execute(
                    f"SELECT COUNT(*) FROM {table} WHERE VALVE_SER_NO = %s AND CYCLE_COMPLETE = 'No'",
                    [valveSerial]
                )
                exists = cursor.fetchone()[0]

                if exists > 0:
                    # Update existing rows AND ensure COUNT_ID is set
                    cursor.execute(
                        f"UPDATE {table} SET {col_updates}, COUNT_ID = %s WHERE VALVE_SER_NO = %s AND CYCLE_COMPLETE = 'No'",
                        col_params + [serial_count, valveSerial]
                    )
                    count = cursor.rowcount
                else:
                    # Insert a new row if none exists (TEST_ID=0 for General/Torque data)
                    # Get common info from master_temp_data to fill the new row
                    cursor.execute("""
                        SELECT STANDARD_NAME, SIZE_NAME, TYPE_NAME, CLASS_NAME, SHELL_MATERIAL_NAME, PRESSURE_UNIT
                        FROM master_temp_data WHERE VALVE_SER_NO = %s LIMIT 1
                    """, [valveSerial])
                    minfo = cursor.fetchone()
                    
                    if minfo:
                        std, size, t_name, cls, mat, punit = minfo
                    else:
                        std = size = t_name = cls = mat = punit = ""

                    # We'll use TEST_ID=0 as a placeholder for torque-only data
                    insert_cols = [
                        "VALVE_SER_NO", "TEST_ID", "TEST_NAME", "CYCLE_COMPLETE", "COUNT_ID",
                        "STANDARD_NAME", "VALVESIZE_NAME", "VALVETYPE_NAME", "VALVECLASS_NAME", "SHELLMATERIAL_NAME", "PRESSURE_UNIT"
                    ]
                    insert_vals = [valveSerial, 0, "Torque/Actuator Data", "No", serial_count, std, size, t_name, cls, mat, punit]
                    
                    # Add our torque columns to the insert
                    # col_params has [val1, val2, val3...] for COL24_NAME, COL24_VALUE, etc.
                    # Actually, col_params has [name1, val1, name2, val2, ...]
                    for i in range(0, len(col_params), 2):
                        idx = 24 + (i // 2)
                        insert_cols.append(f"COL{idx}_NAME")
                        insert_cols.append(f"COL{idx}_VALUE")
                        insert_vals.append(col_params[i])
                        insert_vals.append(col_params[i+1])

                    placeholders = ", ".join(["%s"] * len(insert_cols))
                    col_names = ", ".join(insert_cols)
                    
                    cursor.execute(
                        f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})",
                        insert_vals
                    )
                    count = 1
                
                if table == "pressure_analysis": pa_rows = count
                if table == "temp_pressure_analysis": tpa_rows = count

            print(f"[TORQUE_ACTUATOR] Final status: pa_rows={pa_rows}, tpa_rows={tpa_rows} for {valveSerial}")

            # ---- 3. Update serial_tbl usage count ----
            cursor.execute("SELECT Serial_No FROM serial_tbl WHERE Serial_No = %s", [valveSerial])
            serial_row = cursor.fetchone()
            if serial_row:
                cursor.execute("UPDATE serial_tbl SET Count_No = Count_No + 1 WHERE Serial_No = %s", [valveSerial])
                print(f"[TORQUE_ACTUATOR] Incremented Count_No for {valveSerial}")
            else:
                cursor.execute(
                    "INSERT INTO serial_tbl (Serial_No, Count_No) VALUES (%s, %s)",
                    [valveSerial, 1]
                )
                print(f"[TORQUE_ACTUATOR] Inserted new serial_tbl entry for {valveSerial}")


        return JsonResponse({
            "status": "success",
            "message": f"Torque/Actuator data saved. {pa_rows} row(s) updated in pressure_analysis, {tpa_rows} row(s) updated in temp_pressure_analysis."
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"status": "failure", "message": str(e)}, status=500)

from django.db import connection, transaction

def check_hmi_connection():
    """
    Check if HMI is connected by querying configuration_table
    Returns: bool (True if connected, False otherwise)
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT HMI_CONNECTION FROM configuration_table WHERE id=1")
            result = cursor.fetchone()
            hmi_status = result[0] if result else 'Disabled'
            return hmi_status == 'Enabled'
    except Exception as e:
        print(f"Error checking HMI connection: {e}")
        return False

def check_duplicate_serial_station1(station1_serial):
    """
    Check if station 1 serial number is valid
    Returns: tuple (is_duplicate: bool, None)
    """
    if not station1_serial:
        return False, None
    
    station1_serial = str(station1_serial).strip()
    
    # Since we only have station 1, no duplicate check needed
    return False, None


def save_station1(query, update_values):
    try:
        with connection.cursor() as cursor:
            # Ensure row with ID=1 exists before running the UPDATE query
            cursor.execute("SELECT COUNT(*) FROM master_temp_data WHERE id=1")
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO master_temp_data (id, STATION_STATUS, CYCLE_COMPLETE) VALUES (1, 'Disabled', 'No')")
                
            cursor.execute(query, update_values)
            connection.commit()

            cursor.execute(
                """SELECT INSTRUMENT_SER_NO, `RANGE`, INSTRUMENT_TYPE,
                          CAL_DONE_DATE, CAL_DUE_DATE
                   FROM gauge_details
                   WHERE ACTIVE_STATUS=%s AND STATION_ID=%s""",
                [1, 1]
            )
            values = cursor.fetchall()

            cursor.execute("SELECT VALVE_SER_NO FROM master_temp_data WHERE ID = 1")
            result = cursor.fetchone()
            station1_serial = str(result[0]).strip() if result and result[0] else None

            if values and station1_serial:
                for value in values:
                    print(f"Inserting gauge data: {value}")
                    cursor.execute(
                        """INSERT INTO pressure_gauge_analysis
                           (VALVE_SER_NO, INSTRUMENT_SER_NO, `RANGE`,
                            INSTRUMENT_TYPE, CAL_DUE_DATE, CAL_DONE_DATE, STATION_ID)
                           VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                        [
                            station1_serial,
                            value[0],  # INSTRUMENT_SER_NO
                            value[1],  # RANGE
                            value[2],  # INSTRUMENT_TYPE
                            value[4],  # CAL_DUE_DATE
                            value[3],  # CAL_DONE_DATE
                            1
                        ]
                    )
                    print("Inserted row into pressure_gauge_analysis")
                connection.commit()


            return True

    except Exception as e:
        print("Error while update", str(e))
        return False



def insert_pressure_duration(testname, test_pressure, test_duration, active_testid, diabled_testid, pressureunit, valve_serial_no=None):
    try:        
        # STEP 1: flatten active list
        active = [item[0] for item in active_testid]

        # STEP 2: convert disabled list to int
        disabled = [int(x) for x in diabled_testid if str(x).isdigit()]


        # STEP 3: Find remaining active IDs
        remaining = [tid for tid in active if tid not in disabled]
        print(f"Remaining active tests: {remaining}")
    except Exception as e:
        print(f"ERROR in insert_pressure_duration initialization: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    
    if disabled:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM temp_testing_data_s1 
                WHERE test_id IN %s
                """,
                [tuple(disabled)]
            )
            print("Deleted rows from temp_testing_data for disabled test IDs:", disabled)

    # --- FILTER matched values by remaining list ---
    filtered_testname = []
    filtered_duration = []
    filtered_pressure = []

    for i, tid in enumerate(active):
        if tid not in disabled:
            filtered_testname.append(testname[i])
            filtered_duration.append(test_duration[i])
            filtered_pressure.append(test_pressure[i])

    # Now loop through filtered values
    for i in range(len(remaining)):
        tid = remaining[i]
        tn = filtered_testname[i]
        td = filtered_duration[i]
        tp = filtered_pressure[i]

        # pressure conversion
        if pressureunit.lower() == "psi":
            testing_pressure_psi = tp
            testing_pressure_bar = tp / 14.5
        else:
            testing_pressure_bar = tp
            testing_pressure_psi = tp * 14.5

        testing_duration_unit = "Sec"
        testing_duration_minutes = td / 60
        testing_pressure_kgcm2 = testing_pressure_bar

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT medium, category, pre_col_name, dur_col_name FROM test_type WHERE test_id = %s",
                [tid]
            )
            rows = cursor.fetchall()
            if not rows:
                continue

            for row in rows:

                # -----------------------------
                # ⭐ CHECK IF TEST_ID EXISTS
                # -----------------------------
                cursor.execute(
                    "SELECT COUNT(*) FROM temp_testing_data_s1 WHERE TEST_ID = %s",
                    [tid]
                )
                exists = cursor.fetchone()[0]

                if exists:
                    # -----------------------------
                    # ⭐ UPDATE EXISTING ROW
                    # -----------------------------
                    cursor.execute("""
                        UPDATE temp_testing_data_s1 SET
                            TEST_NAME = %s,
                            TEST_MEDIUM = %s,
                            TEST_CATEGORY = %s,
                            COL_PRE = %s,
                            COL_DUR = %s,
                            TESTING_PR_UNIT = %s,
                            TESTING_PR_BAR = %s,
                            TESTING_PR_PSI = %s,
                            TESTING_PR_KGCM2 = %s,
                            TESTING_DUR_UNIT = %s,
                            TESTING_DUR_SEC = %s,
                            TESTING_DUR_MIN = %s,
                            VALVE_SERIAL_NO = %s
                        WHERE TEST_ID = %s
                    """, [
                        tn, row[0], row[1], row[2], row[3],
                        pressureunit,
                        testing_pressure_bar, testing_pressure_psi, testing_pressure_kgcm2,
                        testing_duration_unit, td, testing_duration_minutes,
                        valve_serial_no,
                        tid
                    ])
                else:
                    # -----------------------------
                    # ⭐ INSERT NEW ROW
                    # -----------------------------
                    cursor.execute("""
                        INSERT INTO temp_testing_data_s1 
                        (TEST_ID,TEST_NAME,TEST_MEDIUM,TEST_CATEGORY,COL_PRE,COL_DUR,
                        TESTING_PR_UNIT,TESTING_PR_BAR,TESTING_PR_PSI,TESTING_PR_KGCM2,
                        TESTING_DUR_UNIT,TESTING_DUR_SEC,TESTING_DUR_MIN,VALVE_SERIAL_NO)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """, [
                        tid, tn, row[0], row[1], row[2], row[3],
                        pressureunit,
                        testing_pressure_bar, testing_pressure_psi, testing_pressure_kgcm2,
                        testing_duration_unit, td, testing_duration_minutes, valve_serial_no
                    ])
                # cursor.execute("select SERIAL_NO from abrs_result_status where SERIAL_NO=%s", [valve_serial_no])
                # serial_no = cursor.fetchone()
                # if serial_no:
                #     print("Serial number already exsting so not changing status in abrs table")
                # else:
                #     cursor.execute("update abrs_result_status set STATUS=%s where SERIAL_NO=%s",[1,valve_serial_no])
                

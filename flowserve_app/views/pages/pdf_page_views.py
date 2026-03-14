from django.shortcuts import render
from django.http import HttpResponse, FileResponse
from flowserve_app.decorators import permission_required
from django.db import connection
from django.conf import settings
from django.template.loader import render_to_string
from datetime import datetime
import os
import base64


def _build_pdf_context(serial_no):
    """
    Build the shared context dict used by both the HTML preview and the
    server-side PDF generator.  Returns (tests_data, common_data).
    """
    tests_data = []
    common_data = {
        'serial_no': serial_no,
        'test_bench_no': '30194',
        'report_no': f"{serial_no}_{datetime.now().year}" if serial_no else '',
        'sale_order_no': '',
        'procedure_no': '',
        'valve_type': '',
        'date_shift': '',
        'size_class': '',
        'tested_by': '',
        'shell_material': '',
        'body_ht_no': '',
        'bonnet_ht_no': '',
        'standard': '',
        'illustration_url': 'images/V1.png',
    }

    if not serial_no:
        return tests_data, common_data

    with connection.cursor() as cursor:
        # Find the latest COUNT_ID for this serial number
        cursor.execute("""
            SELECT MAX(COUNT_ID) FROM pressure_analysis 
            WHERE VALVE_SER_NO = %s
        """, [serial_no])
        latest_count_row = cursor.fetchone()
        latest_count_id = latest_count_row[0] if latest_count_row and latest_count_row[0] else None

        if not latest_count_id:
            return tests_data, common_data

        # Fetch gauge calibration data for this serial number (2 rows)
        cursor.execute("""
            SELECT INSTRUMENT_SER_NO, INSTRUMENT_TYPE, CAL_DUE_DATE 
            FROM pressure_gauge_analysis 
            WHERE VALVE_SER_NO = %s 
            ORDER BY ID ASC
            LIMIT 2
        """, [serial_no])
        gauge_rows = cursor.fetchall()
        
        print(f"DEBUG: Fetched {len(gauge_rows)} gauge rows for serial {serial_no}")
        for idx, row in enumerate(gauge_rows):
            print(f"DEBUG: Gauge row {idx}: {row}")
        
        # Store gauge data: index 0 for HYDRO, index 1 for AIR
        gauge_data_hydro = None
        gauge_data_air = None
        
        if len(gauge_rows) > 0:
            gauge_data_hydro = {
                'serial_no': gauge_rows[0][0] or '',
                'instrument_type': gauge_rows[0][1] or '',
                'due_date': gauge_rows[0][2].strftime('%d/%m/%Y') if gauge_rows[0][2] else ''
            }
            print(f"DEBUG: gauge_data_hydro = {gauge_data_hydro}")
        
        if len(gauge_rows) > 1:
            gauge_data_air = {
                'serial_no': gauge_rows[1][0] or '',
                'instrument_type': gauge_rows[1][1] or '',
                'due_date': gauge_rows[1][2].strftime('%d/%m/%Y') if gauge_rows[1][2] else ''
            }
            print(f"DEBUG: gauge_data_air = {gauge_data_air}")

        # Fetch all tests for this serial number and latest COUNT_ID
        cursor.execute("""
            SELECT * FROM pressure_analysis 
            WHERE VALVE_SER_NO = %s AND COUNT_ID = %s 
            ORDER BY ID ASC
        """, [serial_no, latest_count_id])
        rows = cursor.fetchall()

        if not rows:
            return tests_data, common_data

        columns = [col[0] for col in cursor.description]

        for row in rows:
            data = dict(zip(columns, row))

            # Get test_id to fetch medium from test_type table
            test_id = data.get('TEST_ID')
            test_medium = None
            
            if test_id:
                cursor.execute("""
                    SELECT medium FROM test_type 
                    WHERE test_id = %s
                    LIMIT 1
                """, [test_id])
                medium_row = cursor.fetchone()
                if medium_row:
                    test_medium = medium_row[0]
                    print(f"DEBUG: Test ID {test_id}, Test Name: {data.get('TEST_NAME')}, Medium: {test_medium}")

            # Process dynamic parameters (Date, Shift, etc.)
            dynamic_params = {}
            for i in range(1, 49):
                name_key = f'COL{i}_NAME'
                val_key = f'COL{i}_VALUE'
                if name_key in data and val_key in data:
                    p_name = data.get(name_key)
                    p_val = data.get(val_key)
                    if p_name:
                        dynamic_params[p_name.strip()] = p_val

            # Calculate observed time
            obs_time = ''
            start_time = data.get('START')
            end_time = data.get('END')
            if start_time and end_time:
                try:
                    duration = end_time - start_time
                    obs_time = f"{int(duration.total_seconds())} Sec"
                except Exception:
                    pass

            # Graph Image Retrieval
            test_id = data.get('TEST_ID', '')
            test_name = data.get('TEST_NAME', '')
            count_id = data.get('COUNT_ID', '1') or '1'

            graph_image_base64 = None
            graphs_folder = settings.GRAPH_EXPORT_PATH
            valve_graph_folder = os.path.join(graphs_folder, str(serial_no))

            if test_id and test_name:
                norm_test_name = test_name.replace(' ', '_')
                graph_filename = f"{serial_no}_{count_id}_Test{test_id}_{norm_test_name}.png"
                graph_filepath = os.path.join(valve_graph_folder, graph_filename)

                if not os.path.exists(graph_filepath) and os.path.exists(valve_graph_folder):
                    try:
                        files = os.listdir(valve_graph_folder)
                        for file in files:
                            f_lower = file.lower()
                            pattern = f"{serial_no}_{count_id}_test{test_id}_".lower()
                            if f_lower.startswith(pattern):
                                graph_filepath = os.path.join(valve_graph_folder, file)
                                break
                    except Exception:
                        pass

                if os.path.exists(graph_filepath):
                    try:
                        with open(graph_filepath, 'rb') as f:
                            image_data = f.read()
                            graph_image_base64 = f"data:image/png;base64,{base64.b64encode(image_data).decode('utf-8')}"
                    except Exception:
                        pass

            # Convert pressure values to integers
            set_pressure_val = data.get('SET_PRESSURE', '')
            actual_pressure_val = data.get('ACTUAL_PRESSURE', '')
            pressure_unit = data.get('PRESSURE_UNIT', '')
            
            # Format as integer if numeric
            try:
                set_pressure_str = f"{int(float(set_pressure_val))} {pressure_unit}" if set_pressure_val else ''
            except (ValueError, TypeError):
                set_pressure_str = f"{set_pressure_val} {pressure_unit}"
            
            try:
                obs_pressure_str = f"{int(float(actual_pressure_val))} {pressure_unit}" if actual_pressure_val else ''
            except (ValueError, TypeError):
                obs_pressure_str = f"{actual_pressure_val} {pressure_unit}"
            
            # Determine which gauge data to use based on test medium
            gauge_data = None
            if test_medium:
                if test_medium.upper() == 'HYDRO':
                    gauge_data = gauge_data_hydro
                    print(f"DEBUG: Assigned HYDRO gauge data: {gauge_data}")
                elif test_medium.upper() == 'AIR':
                    gauge_data = gauge_data_air
                    print(f"DEBUG: Assigned AIR gauge data: {gauge_data}")
                else:
                    print(f"DEBUG: Unknown medium '{test_medium}', no gauge data assigned")
            else:
                print(f"DEBUG: No test_medium found for test {data.get('TEST_NAME')}")
            
            test_obj = {
                'test_type': test_name,
                'set_time': f"{data.get('SET_TIME', '')} {data.get('SET_TIME_UNIT', '')}",
                'set_pressure': set_pressure_str,
                'obs_pressure': obs_pressure_str,
                'obs_time': obs_time,
                'test_result': data.get('VALVE_STATUS', ''),
                'graph_image_base64': graph_image_base64,
                'test_orientation': dynamic_params.get('Test Orientation', ''),
                'valve_bore_orientation': dynamic_params.get('Valve Bore Orientation', ''),
                'stem_position': dynamic_params.get('Stem Orientation', ''),
                'test_medium': test_medium,  # Add test medium
                'gauge_data': gauge_data  # Add gauge data for this specific test
            }
            tests_data.append(test_obj)

            common_data.update({
                'sale_order_no': dynamic_params.get('Sales Order No', ''),
                'procedure_no': dynamic_params.get('Procedure No', ''),
                'valve_type': data.get('VALVETYPE_NAME', ''),
                'size_class': f"{data.get('VALVESIZE_NAME', '')} & {data.get('VALVECLASS_NAME', '')}",
                'shell_material': data.get('SHELLMATERIAL_NAME', ''),
                'body_ht_no': dynamic_params.get('Body Heat No', ''),
                'bonnet_ht_no': dynamic_params.get('Bottom Heat No', '') or dynamic_params.get('Bonnet Heat No', ''),
                'tested_by': dynamic_params.get('Tested By', ''),
                'standard': dynamic_params.get('Customer', ''),  # Changed from STANDARD_NAME to Customer
                'date_shift': f"{dynamic_params.get('Date', datetime.now().strftime('%d/%m/%Y'))} & {dynamic_params.get('Shift', 'Shift 1')}",
            })

            # Check for explicitly selected gauges (COL40 - COL45)
            # COL40: Hydro_Gauge_1, COL41: Hydro_Gauge_2
            # COL42: Air_Gauge_1,   COL43: Air_Gauge_2
            # COL44: Hydro_Transducer, COL45: Air_Transducer
            if 'calibration_details' not in common_data:
                calibration_details = []
                selected_gauges = []
                
                gauge_keys = [
                    'Hydro_Gauge_1', 'Hydro_Gauge_2', 
                    'Air_Gauge_1', 'Air_Gauge_2', 
                    'Hydro_Transducer', 'Air_Transducer'
                ]
                
                for key in gauge_keys:
                    val = dynamic_params.get(key, '')
                    if val and val != "N/A":
                        # Value format is typically: "SerialNo - Type"
                        serial_part = val.split(' - ')[0].strip()
                        if serial_part:
                            selected_gauges.append({
                                'key': key,
                                'serial_no': serial_part
                            })
                
                if selected_gauges:
                    # Deduplicate serials just for the DB query to avoid redundancy
                    unique_serials = list(dict.fromkeys([g['serial_no'] for g in selected_gauges]))
                    
                    placeholders = ', '.join(['%s'] * len(unique_serials))
                    query = f"""
                        SELECT INSTRUMENT_SER_NO, INSTRUMENT_TYPE, CAL_DUE_DATE
                        FROM gauge_details
                        WHERE INSTRUMENT_SER_NO IN ({placeholders})
                    """
                    cursor.execute(query, unique_serials)
                    db_gauges = cursor.fetchall()
                    
                    # Create a lookup dictionary casting keys to string to prevent mismatch
                    gauge_lookup = {}
                    for g_serial, g_type, g_date in db_gauges:
                        # User Request explicitly asked:
                        # "in the S.No show the gauges serial no and show the type in the instrument type column"
                        g_serial_str = str(g_serial).strip()
                        g_date_str = g_date.strftime('%d/%m/%Y') if g_date else ''
                        gauge_lookup[g_serial_str] = {
                            'serial_no': g_serial_str,
                            'instrument_type': g_type or '',
                            'due_date': g_date_str
                        }
                    
                    # Generate a row for EACH selected input (even if same gauge)
                    for item in selected_gauges:
                        serial_str = str(item['serial_no']).strip()
                        if serial_str in gauge_lookup:
                            calibration_details.append({
                                'serial_no': gauge_lookup[serial_str]['serial_no'],
                                'instrument_type': gauge_lookup[serial_str]['instrument_type'],
                                'due_date': gauge_lookup[serial_str]['due_date']
                            })
                
                common_data['calibration_details'] = calibration_details

            ill_val = dynamic_params.get('Illustration')
            if ill_val:
                common_data['illustration_url'] = f"images/{ill_val}.png"

    return tests_data, common_data


@permission_required("Graph")
def pdf_page(request):
    """
    When ?download=true  → generate PDF server-side with WeasyPrint and
                           stream it directly as a binary file download.
    Otherwise            → render the HTML preview page (pdf.html).
    """
    serial_no_raw = request.GET.get('serial_no', '')
    serial_no = serial_no_raw.strip() if serial_no_raw else ''
    download = request.GET.get('download') == 'true'

    tests_data, common_data = _build_pdf_context(serial_no)

    # ------------------------------------------------------------------ #
    #  SERVER-SIDE PDF GENERATION (download=true)                          #
    # ------------------------------------------------------------------ #
    if download:
        try:
            from weasyprint import HTML as WeasyprintHTML, CSS
            from django.http import JsonResponse

            context = {
                'download': False,   # no JS autoprint inside the server-rendered html
                'tests': tests_data,
                **common_data,
            }

            # Render the same pdf.html template to a string
            html_string = render_to_string('pdf.html', context, request=request)

            # Get count_id from the database
            count_id = None
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT MAX(COUNT_ID) FROM pressure_analysis 
                    WHERE VALVE_SER_NO = %s
                """, [serial_no])
                count_row = cursor.fetchone()
                count_id = count_row[0] if count_row and count_row[0] else '1'

            # Build folder structure: D/reports/
            reports_dir = os.path.join('D:', 'reports')
            
            # Ensure folder exists
            os.makedirs(reports_dir, exist_ok=True)

            # Build filename: Report_{valve_serial}_{count}.pdf
            filename = f"Report_{serial_no}_{count_id}.pdf"
            filepath = os.path.join(reports_dir, filename)

            # Generate PDF from html string
            WeasyprintHTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf(filepath)

            # Return success response instead of file download
            return JsonResponse({
                'success': True,
                'message': 'Report saved successfully',
                'filepath': filepath,
                'filename': filename
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            # Return error response
            return JsonResponse({
                'success': False,
                'message': f'Error generating report: {str(e)}'
            }, status=500)

    # ------------------------------------------------------------------ #
    #  HTML PREVIEW (no download param or download=false)                  #
    # ------------------------------------------------------------------ #
    context = {
        'download': False,
        'tests': tests_data,
        **common_data,
    }
    return render(request, 'pdf.html', context)

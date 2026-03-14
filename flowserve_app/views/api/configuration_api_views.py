from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from flowserve_app.decorators import permission_required, superuser_required, login_required
from pymodbus.client import ModbusTcpClient
import json
import pyodbc

from flowserve_app.services.user_config_service import (
get_abrs_field_db, update_hmi_enabled, update_hmi_disabled, 
update_abrs_enabled, update_abrs_disabled, get_hmi_abrs_status, get_all_toggle_value, get_pdf_status,
get_csv_status, update_backup_status, save_report_path_db, save_abrs_field_db, get_alarmname_s1, get_recent_alarms,
insert_hmi_add, insert_abrs, get_hmi_abrs_value, get_hmi_address, get_gauge_calibration_alerts
)
from flowserve_app.services.shell_material_service import (
    check_shell_material_pressures, check_master_duration_data, check_master_degree_data
)


# Dynamic HMI client management
TestleadSmartsyncx = None
_current_hmi_address = None

# TestleadSmartsyncx = ModbusTcpClient('127.0.0.1')

def update_hmi_client():
    """Update global HMI client if address changed"""
    global TestleadSmartsyncx, _current_hmi_address
    
    try:
        # Get current address from DB
        new_address = get_hmi_address()
        
        if not new_address:
            print('WARNING: HMI address is None or empty')
            return
        
        # Strip whitespace
        new_address = new_address.strip()
        
        if not new_address:
            print('WARNING: HMI address is empty after stripping')
            return
        
        # If address changed or client doesn't exist, create new client
        if _current_hmi_address != new_address or TestleadSmartsyncx is None:
            print(f'HMI address changed from {_current_hmi_address} to {new_address}')
            
            # Close old connection if exists
            if TestleadSmartsyncx is not None:
                try:
                    TestleadSmartsyncx.close()
                except:
                    pass
            
            # Create new client with timeout
            TestleadSmartsyncx = ModbusTcpClient(new_address, timeout=1)
            _current_hmi_address = new_address
            print(f'Created new HMI client for {new_address}')
        
    except Exception as e:
        print(f'ERROR updating HMI client: {e}')

# Initialize on module load
update_hmi_client()

class ABRSDatabase:
    def __init__(self):
        self.server = None
        self.database = None
        self.driver = '{ODBC Driver 17 for SQL Server}'
    
    def get_connection_string(self):
        """Build connection string"""
        if not self.server or not self.database:
            raise ValueError("ABRS server and database must be configured")
        
        return (
            f'DRIVER={self.driver};'
            f'SERVER={self.server};'
            f'DATABASE={self.database};'
            'Trusted_Connection=yes;'
            'TrustServerCertificate=yes;'
        )
    
    def test_connection(self):
        """Test ABRS database connection - creates fresh connection each time"""
        try:
            # Check if config is set
            if not self.server or not self.database:
                return False
            
            # Create a new connection and test it
            with pyodbc.connect(self.get_connection_string()) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result is not None
                
        except Exception as e:
            # Silently return False without printing error
            return False

# Global instance
abrs_db = ABRSDatabase()

# Dynamic ABRS connection management
_current_abrs_config = None

def update_abrs_connection():
    """Update ABRS connection if configuration changed"""
    global abrs_db, _current_abrs_config
    
    try:
        # Get current ABRS config from DB
        abrs_info = get_hmi_abrs_value()
        
        if not abrs_info:
            print('WARNING: ABRS configuration is None or empty')
            abrs_db.server = None
            abrs_db.database = None
            return
        
        # Extract config values from DB only
        new_config = {
            'host': abrs_info[1],
            'port': abrs_info[2],
            'database': abrs_info[3],
            'username': abrs_info[4],
            'password': abrs_info[5]
        }
        
        # If config changed, update ABRS instance
        if _current_abrs_config != new_config:
            # print(f'ABRS config changed from {_current_abrs_config} to {new_config}')
            
            # Update ABRS database instance with values from DB only (no fallback)
            abrs_db.server = new_config['host']
            abrs_db.database = new_config['database']
            
            _current_abrs_config = new_config
            # print(f'Updated ABRS connection to {abrs_db.server}/{abrs_db.database}')
        
    except Exception as e:
        print(f'ERROR updating ABRS connection: {e}')
        abrs_db.server = None
        abrs_db.database = None


@login_required
@csrf_exempt
def get_hmi_abrs_api(request):
    # HMI connection check
    alarm_s1_value = 0
    # alarm_s2_value = 0
    alarm_s1_name = None
    # alarm_s2_name = None
    recent_alarms = []
    
    # Update HMI client if address changed
    update_hmi_client()
    
    try:
        connection = TestleadSmartsyncx.read_holding_registers(2000, 1)
        alarm_s1_result = TestleadSmartsyncx.read_holding_registers(2035, 1)  # station1
        # alarm_s2_result = TestleadSmartsyncx.read_holding_registers(2133, 1)  # station2
        
        if connection.isError():
            hmi_status = 0
            update_hmi_disabled()
        else:
            hmi_status = 1
            update_hmi_enabled()
            
            # Get alarm values from HMI
            if not alarm_s1_result.isError():
                alarm_s1_value = alarm_s1_result.registers[0]
            # if not alarm_s2_result.isError():
            #     alarm_s2_value = alarm_s2_result.registers[0]
            
    except Exception as e:
        print(f'HMI connection error: {e}')
        hmi_status = 0
        update_hmi_disabled()
        

    # ABRS connection check
    # Update ABRS connection if config changed
    update_abrs_connection()
    
    try:
        abrs_connection = 1 if abrs_db.test_connection() else 0
        
        if abrs_connection == 0:
            update_abrs_disabled()
        else:
            update_abrs_enabled()
            
    except Exception as e:
        abrs_connection = 0
        update_abrs_disabled()
    
    # Process alarms if HMI is connected
    if hmi_status == 1:
        # Process Station 1 alarm
        if alarm_s1_value > 0:
            alarms_s1 = get_alarmname_s1(alarm_s1_value)
            if alarms_s1 and len(alarms_s1) > 0:
                alarm_s1_name = alarms_s1[0][0]  # First alarm name
        
        # Process Station 2 alarm
        # if alarm_s2_value > 0:
        #     alarms_s2 = get_alarmname_s2(alarm_s2_value)
        #     if alarms_s2 and len(alarms_s2) > 0:
        #         alarm_s2_name = alarms_s2[0][0]  # First alarm name
    
    # Get recent 4 alarms for display (always fetch from DB regardless of HMI connection)
    try:
        rows = get_recent_alarms(4)
        
        from datetime import datetime, timezone, timedelta
        for row in rows:
                alarm_name = row[0]
                alarm_time = row[1]
                
                # Calculate relative time (treating database times as local time)
                from datetime import datetime, timezone, timedelta
                
                # Get current time in local timezone (IST)
                now = datetime.now()
                
                # If alarm_time is timezone-naive, treat it as local time
                if alarm_time.tzinfo is not None:
                    alarm_time = alarm_time.replace(tzinfo=None)
                    
                # Calculate time difference
                diff = now - alarm_time
                seconds = diff.total_seconds()
                

                if seconds < 60:
                    time_ago = "just now"
                elif seconds < 3600:  # Less than 1 hour
                    minutes = int(seconds / 60)
                    time_ago = f"{minutes} min ago" if minutes == 1 else f"{minutes} mins ago"
                elif seconds < 86400:  # Less than 1 day
                    hours = int(seconds / 3600)
                    time_ago = f"{hours} hour ago" if hours == 1 else f"{hours} hours ago"
                else:  # 1 day or more
                    days = int(seconds / 86400)
                    time_ago = f"{days} day ago" if days == 1 else f"{days} days ago"
                
                recent_alarms.append({
                    'alarm_name': alarm_name,
                    'time_ago': time_ago
                })
    except Exception as e:
        print(f"Error getting recent alarms: {e}")

    # Get gauge calibration alerts (1-10 days due)
    gauge_calibration_alerts = []
    try:
        gauge_calibration_alerts = get_gauge_calibration_alerts()
    except Exception as e:
        print(f"Error getting gauge calibration alerts: {e}")


    return JsonResponse({
        "hmi_connection": hmi_status,
        "abrs_connection": abrs_connection,
        "alarm_s1": alarm_s1_value,
        "alarm_s1_name": alarm_s1_name,
        # "alarm_s2": alarm_s2_value,
        # "alarm_s2_name": alarm_s2_name,
        "recent_alarms": recent_alarms,
        "gauge_calibration_alerts": gauge_calibration_alerts
    })



# graph toggle

@login_required
@csrf_exempt
def update_graph_toggle(request):
    data = json.loads(request.body)
    status = data.get("graph_toggle")
    get_hmi_abrs_status(status)
    
    return JsonResponse({"graph_report": status})

@login_required
@csrf_exempt
def update_pdf_toggle(request):
    data = json.loads(request.body)
    status = data.get("pdf_toggle")
    get_pdf_status(status)

    return JsonResponse({"pdf_report": status})

@login_required
@csrf_exempt
def update_csv_toggle(request):
    data = json.loads(request.body)
    status = data.get("csv_toggle")
    get_csv_status(status)

    return JsonResponse({"csv_report": status})

@login_required
@csrf_exempt
def update_backup_toggle(request):
    data = json.loads(request.body)
    status = data.get("backup_toggle")
    update_backup_status(status)

    return JsonResponse({"auto_backup": status})

@login_required
@csrf_exempt
def get_all_toggle(request):        
    report = get_all_toggle_value()
    hmi_abrs_info = get_hmi_abrs_value()
    
    if report:
        all_reports = {
            "graph_pdf_report": report[0],
            "vtr_pdf_report": report[1],
            "vtr_csv_report": report[2],
            "report_path": report[3],
            "auto_db_backup": report[4]
        }
    if hmi_abrs_info:
        all_info = {
            "hmi_ip": hmi_abrs_info[0],
            "abrs_host": hmi_abrs_info[1],
            "abrs_port": hmi_abrs_info[2],
            "abrs_db": hmi_abrs_info[3],
            "abrs_username": hmi_abrs_info[4],
            "abrs_password": hmi_abrs_info[5]
        }
        return JsonResponse({"status": "success", "all_reports": all_reports, "abrs_connection": all_info})

  
@login_required
@csrf_exempt
def save_report_path(request):
    data = json.loads(request.body)
    report_path = data.get("report_path")
    save_report_path_db(report_path)

    return JsonResponse({"report_path": report_path})

@login_required
@csrf_exempt
def save_abrs_field(request):
    if request.method != "POST":
        return JsonResponse({"status": "error"})

    data = json.loads(request.body)
    name = data.get("name")
    value = data.get("value")

    save_abrs_field_db(name, value)

    return JsonResponse({"status": "success"})


@login_required
@csrf_exempt
def get_abrs_values(request):
    data = get_abrs_field_db()
    return JsonResponse(data)


@csrf_exempt
def connect_hmi(request):
    global _current_hmi_address
    
    data = json.loads(request.body)
    hmi_ip = data.get('ip')
    
    # Save to database
    insert_hmi_add(hmi_ip)
    
    # Force reconnection on next request by clearing cached address
    _current_hmi_address = None
    print(f'HMI address updated to {hmi_ip}, will reconnect on next request')
    
    return JsonResponse({"status": "success"})


@csrf_exempt
def connect_abrs(request):
    data = json.loads(request.body)
    abrs_host = data.get('host')
    abrs_port = data.get('port')
    abrs_db_name = data.get('database')
    abrs_username = data.get('username')
    abrs_password = data.get('password')
    
    insert_abrs(abrs_host, abrs_port, abrs_db_name, abrs_username, abrs_password)
    return JsonResponse({"status": "success"})


@login_required
@csrf_exempt
def validate_before_test(request):
    """
    Comprehensive validation before allowing New Test or Continue Test
    Checks:
    1. HMI Connection
    2. Gauge Calibration (overdue gauges)
    3. Shell Material Pressures (0 or NULL)
    """
    validation_result = {
        'can_proceed': True,
        'issues': [],
        'hmi_status': None,
        'gauge_alerts': [],
        'material_issues': []
    }
    
    # Update HMI client if address changed
    update_hmi_client()
    
    # 1. CHECK HMI CONNECTION
    try:
        connection = TestleadSmartsyncx.read_holding_registers(2000, 1)
        
        if connection.isError():
            hmi_status = 0
            update_hmi_disabled()
        else:
            hmi_status = 1
            update_hmi_enabled()
            
    except Exception as e:
        print(f'HMI connection error: {e}')
        hmi_status = 0
        update_hmi_disabled()
    
    validation_result['hmi_status'] = hmi_status
    
    if hmi_status == 0:
        validation_result['can_proceed'] = False
        validation_result['issues'].append({
            'type': 'hmi_disconnected',
            'title': 'HMI Not Connected',
            'message': 'Please connect HMI before proceeding with the test.'
        })
    
    # 2. CHECK GAUGE CALIBRATION ALERTS (overdue or due within 10 days)
    try:
        gauge_alerts = get_gauge_calibration_alerts()
        
        if gauge_alerts:
            validation_result['gauge_alerts'] = gauge_alerts
            validation_result['can_proceed'] = False
            
            # Build gauge alert message with color coding
            gauge_list = ""
            
            for alert in gauge_alerts:
                days_left = alert['days_left']
                status_color = '#dc3545' if days_left < 0 else '#ffc107'  # red for overdue, yellow for upcoming
                status_badge = '🔴 OVERDUE' if days_left < 0 else '⚠️ DUE SOON'
                
                gauge_list += f"""
                <div style="
                  margin-bottom: 8px;
                  padding: 10px;
                  background: {status_color}20;
                  border-left: 3px solid {status_color};
                  border-radius: 4px;
                ">f
                  <strong>{alert['instrument_ser_no']}</strong> - {status_badge}<br>
                  <small>Due: {alert['cal_due_date']} ({alert['days_left']} days)</small>
                </div>
                """
            
            validation_result['issues'].append({
                'type': 'gauge_overdue',
                'title': 'Gauge Calibration Alert',
                'message': f'The following gauges need attention:<br>{gauge_list}<br>Please update calibration dates before proceeding.'
            })
    except Exception as e:
        print(f"Error checking gauge calibration: {e}")
    
    # 3. CHECK SHELL MATERIAL PRESSURES
    try:
        material_check = check_shell_material_pressures()
        
        if material_check['has_issues']:
            validation_result['material_issues'] = material_check['materials']
            validation_result['can_proceed'] = False
            
            # Build material alert message
            material_list = "<br>".join([
                f"<strong>{mat['name']}</strong> (ID: {mat['id']})"
                for mat in material_check['materials']
            ])
            
            validation_result['issues'].append({
                'type': 'material_pressure_invalid',
                'title': 'Shell Material Pressure Issue',
                'message': f'The following materials have invalid pressure values (0 or NULL):<br>{material_list}<br><br>Please update pressure values before proceeding.'
            })
    except Exception as e:
        print(f"Error checking shell material pressures: {e}")

    # 4. CHECK MASTER DURATION DATA
    try:
        duration_check = check_master_duration_data()
        
        if duration_check['has_issues']:
            validation_result['can_proceed'] = False
            
            # Build duration alert message
            # Limit to first 10 items to avoid huge alerts
            duration_list_items = duration_check['durations'][:10]
            duration_list = "<br>".join([
                f"<strong>Standard: {item['standard']}, Size: {item['size']}</strong>"
                for item in duration_list_items
            ])
            
            if len(duration_check['durations']) > 10:
                duration_list += f"<br>...and {len(duration_check['durations']) - 10} more"
            
            validation_result['issues'].append({
                'type': 'duration_data_invalid',
                'title': 'Duration Data Missing',
                'message': f'The following combinations have missing duration values (NULL or 0):<br>{duration_list}<br><br>Please check Master Duration Data.'
            })
    except Exception as e:
        print(f"Error checking duration data: {e}")

    # 5. CHECK MASTER DEGREE DATA
    try:
        degree_check = check_master_degree_data()
        
        if degree_check['has_issues']:
            validation_result['can_proceed'] = False
            
            # Build degree alert message
            degree_list_items = degree_check['degrees'][:10]
            degree_list = "<br>".join([
                f"<strong>Type: {item['type']}, Size: {item['size']}</strong>"
                for item in degree_list_items
            ])
            
            if len(degree_check['degrees']) > 10:
                degree_list += f"<br>...and {len(degree_check['degrees']) - 10} more"
            
            validation_result['issues'].append({
                'type': 'degree_data_invalid',
                'title': 'Degree Data Missing',
                'message': f'The following combinations have missing degree values (NULL):<br>{degree_list}<br><br>Please check Master Degree Data.'
            })
    except Exception as e:
        print(f"Error checking degree data: {e}")
    
    return JsonResponse(validation_result)

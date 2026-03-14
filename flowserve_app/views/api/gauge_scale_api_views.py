"""
API Views for Gauge Scale Service
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
import json
from flowserve_app.services.gauge_scale_service import get_gauge_scale, get_gauge_scale_from_valve_class_name, get_available_class_ratings, get_available_pressure_units,get_gauge_config_mapping


@csrf_exempt
@require_http_methods(["POST"])
def get_gauge_scale_api(request):
    """
    API endpoint to get gauge scale based on pressure unit, class rating, and medium.
    
    Expected JSON payload:
    {
        "pressure_unit": "bar",  // or "psi", "kg/cm2g"
        "class_rating": "#150",  // or "#300", "#600", "#900", "#1500"
        "valve_serial": "12345", // optional - to check medium from temp_testing_data_s1
        "test_id": 1             // optional - to identify specific test when multiple tests exist
    }
    
    Returns:
    {
        "gauge_scale": 70,  // calculated gauge scale
        "status": "success"
    }
    """
    try:
        from django.db import connection
        
        data = json.loads(request.body)
        
        pressure_unit = data.get('pressure_unit', '').strip()
        class_rating = data.get('class_rating', '').strip()
        valve_serial = data.get('valve_serial', '').strip()
        test_id = data.get('test_id')
        
        if not pressure_unit:
            return JsonResponse({
                'status': 'error',
                'message': 'Pressure unit is required'
            }, status=400)
        
        if not class_rating:
            return JsonResponse({
                'status': 'error',
                'message': 'Class rating is required'
            }, status=400)
        
        # Check medium from temp_testing_data_s1 if valve_serial is provided
        medium = None
        if valve_serial:
            with connection.cursor() as cursor:
                # Query for the specific valve serial and test_id if provided
                if test_id:
                    cursor.execute("""
                        SELECT TEST_MEDIUM FROM temp_testing_data_s1
                        WHERE VALVE_SERIAL_NO = %s AND TEST_ID = %s
                        LIMIT 1
                    """, [valve_serial, test_id])
                else:
                    # If no test_id, get the most recent one (last inserted)
                    cursor.execute("""
                        SELECT TEST_MEDIUM FROM temp_testing_data_s1
                        WHERE VALVE_SERIAL_NO = %s
                        ORDER BY TEST_ID DESC
                        LIMIT 1
                    """, [valve_serial])
                
                row = cursor.fetchone()
                if row:
                    medium = row[0]
        
        # Calculate gauge scale based on medium and class rating
        if medium and medium.lower().strip() == 'air':
            # Air medium - fixed scale of 250 PSI for all class ratings
            if pressure_unit.lower() in ['bar', 'kg/cm2g']:
                gauge_scale = 20  # Fixed BAR scale for air
            else:  # PSI
                gauge_scale = 250  # Fixed PSI scale for air
        else:
            # Hydro/Water medium - use standard class-based scale
            gauge_scale = get_gauge_scale(pressure_unit, class_rating)
            gauge_config_mapping = get_gauge_config_mapping()
        
        return JsonResponse({
            'gauge_scale': gauge_scale,
            'gauge_config': gauge_config_mapping,
            'pressure_unit': pressure_unit,
            'class_rating': class_rating,
            'medium': medium,
            'status': 'success'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON in request body'
        }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
        
        return JsonResponse({
            'gauge_scale': gauge_scale,
            'pressure_unit': pressure_unit,
            'class_rating': class_rating,
            'medium': medium,
            'status': 'success'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON in request body'
        }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def get_gauge_scale_from_valve_class_api(request):
    """
    API endpoint to get gauge scale based on valve class name and pressure unit.
    
    Expected JSON payload:
    {
        "valve_class_name": "Class 150",  // or "150#", "#300", etc.
        "pressure_unit": "bar"             // or "psi", "kg/cm2g"
    }
    
    Returns:
    {
        "gauge_scale": 70,  // calculated gauge scale
        "status": "success"
    }
    """
    try:
        data = json.loads(request.body)
        
        valve_class_name = data.get('valve_class_name', '').strip()
        pressure_unit = data.get('pressure_unit', '').strip()
        
        if not valve_class_name:
            return JsonResponse({
                'status': 'error',
                'message': 'Valve class name is required'
            }, status=400)
        
        if not pressure_unit:
            return JsonResponse({
                'status': 'error',
                'message': 'Pressure unit is required'
            }, status=400)
        
        # Calculate gauge scale
        gauge_scale = get_gauge_scale_from_valve_class_name(valve_class_name, pressure_unit)
        
        return JsonResponse({
            'gauge_scale': gauge_scale,
            'valve_class_name': valve_class_name,
            'pressure_unit': pressure_unit,
            'status': 'success'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON in request body'
        }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


def get_available_options_api(request):
    """
    API endpoint to get available class ratings and pressure units.
    
    Returns:
    {
        "class_ratings": ["#150", "#300", "#600", "#900", "#1500"],
        "pressure_units": ["bar", "psi", "kg/cm2g"],
        "status": "success"
    }
    """
    try:
        class_ratings = get_available_class_ratings()
        pressure_units = get_available_pressure_units()
        
        return JsonResponse({
            'class_ratings': class_ratings,
            'pressure_units': pressure_units,
            'status': 'success'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
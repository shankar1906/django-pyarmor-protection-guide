from django.http import JsonResponse
from flowserve_app.decorators import permission_required
from flowserve_app.services.gauge_config_service import (
    get_gauge_config_mapping,
    get_gauge_color_mapping,
    get_gauge_class_mapping,
    save_gauge_config
)
from flowserve_app.services.valve_class_service import get_all_valve_classes
import json

@permission_required("Gauge Config")
def get_gauge_config_api(request):
    """
    GET endpoint to retrieve all gauge configurations.
    """
    if request.method != "GET":
        return JsonResponse({"success": False, "error": "Invalid method"}, status=405)
    
    try:
        mapping = get_gauge_config_mapping()
        colors = get_gauge_color_mapping()
        classes_config = get_gauge_class_mapping()
        
        # Also get all available valve classes for dropdowns
        all_valve_classes = get_all_valve_classes()
        valve_classes_list = [row[2] for row in all_valve_classes] # row[2] is CLASS_NAME
        
        return JsonResponse({
            "success": True,
            "mapping": mapping,
            "colors": colors,
            "classes_config": classes_config,
            "available_valve_classes": valve_classes_list
        })
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

@permission_required("Gauge Config")
def save_gauge_config_api(request):
    """
    POST endpoint to save gauge configuration.
    """
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid method"}, status=405)
    
    try:
        data = json.loads(request.body)
        
        mapping_data = data.get('mapping', {})
        color_data = data.get('colors', [])
        class_data = data.get('classes', [])
        
        save_gauge_config(mapping_data, color_data, class_data)
        
        return JsonResponse({
            "success": True, 
            "message": "Configuration saved successfully"
        })
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

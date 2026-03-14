from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

from flowserve_app.decorators import permission_required
from flowserve_app.services.form_data2_service import (
    get_form_data2_by_valve_type,
    save_form_data2,
    get_all_form_data2_records,
    bulk_delete_form_data2_by_valve_types,
    delete_form_data2_for_valve_type
)

@permission_required("Form Data")
@require_http_methods(["GET"])
def list_all_configs_api(request):
    """
    GET endpoint to retrieve unique valve types that have configurations.
    """
    try:
        records = get_all_form_data2_records()
        return JsonResponse({"records": records})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@permission_required("Form Data")
@require_http_methods(["GET"])
def get_form_data2_api(request, valve_type_id):
    """
    GET endpoint to retrieve individual field entries for a specific valve type.
    """
    try:
        fields = get_form_data2_by_valve_type(valve_type_id)
        return JsonResponse({"fields": fields})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@permission_required("Form Data")
@require_http_methods(["POST"])
@csrf_exempt
def save_form_data2_api(request):
    """
    POST endpoint to save multiple fields for one valve type.
    """
    try:
        data = json.loads(request.body or "{}")
        valve_type_id = data.get("valve_type_id")
        items = data.get("items", [])
        is_update = data.get("is_update", False)
        
        if not valve_type_id:
            return JsonResponse({"error": "Valve Type ID is required."}, status=400)

        result = save_form_data2(valve_type_id, items, is_update=is_update)
        if result.get('success'):
            return JsonResponse({"message": result.get('message')})
        else:
            return JsonResponse({"error": result.get('error')}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@permission_required("Form Data")
@require_http_methods(["POST"])
@csrf_exempt
def bulk_delete_api(request):
    """
    POST endpoint to delete all configurations for multiple valve type IDs.
    """
    try:
        data = json.loads(request.body or "{}")
        ids = data.get("ids", []) # These are Valve Type IDs
        if not ids:
            return JsonResponse({"error": "No Valve Type IDs provided"}, status=400)
            
        result = bulk_delete_form_data2_by_valve_types(ids)
        if result.get('success'):
            return JsonResponse({"message": result.get('message')})
        else:
            return JsonResponse({"error": result.get('error')}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@permission_required("Form Data")
@require_http_methods(["POST"])
@csrf_exempt
def delete_valve_type_configs_api(request, valve_type_id):
    """
    POST endpoint to delete all configurations for a single valve type.
    """
    try:
        result = delete_form_data2_for_valve_type(valve_type_id)
        if result.get('success'):
            return JsonResponse({"message": result.get('message')})
        else:
            return JsonResponse({"error": result.get('error')}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

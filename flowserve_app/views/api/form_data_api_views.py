from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

from flowserve_app.decorators import permission_required
from flowserve_app.services.form_data_service import (
    get_all_form_data,
    check_duplicate_form_name,
    update_form_data_entry,
    delete_form_data_entry
)

@permission_required("Form Data")
@require_http_methods(["GET"])
def get_form_data_api(request):
    """
    GET endpoint to retrieve all form data records.
    """
    try:
        rows = get_all_form_data()
        form_data_list = []
        for row in rows:
            form_data_list.append({
                "id": row[0],
                "form_name": row[1],
                "status": row[2]
            })
        
        return JsonResponse({"form_data": form_data_list})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@permission_required("Form Data")
@require_http_methods(["POST"])
@csrf_exempt
def delete_form_data_api(request, form_id):
    """
    POST endpoint to delete a form data entry.
    """
    try:
        delete_form_data_entry(form_id)
        return JsonResponse({"message": "Form Data deleted successfully!"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@permission_required("Form Data")
@require_http_methods(["POST"])
@csrf_exempt
def update_form_data_api(request):
    """
    POST endpoint to bulk update form data entries.
    """
    try:
        data = json.loads(request.body or "{}")
        items = data.get("items", [])
        
        if not isinstance(items, list):
            return JsonResponse({"error": "Invalid payload format."}, status=400)

        # Validation phase
        seen_names = set()
        for idx, item in enumerate(items, start=1):
            name = (item.get("form_name") or "").strip()
            if not name:
                return JsonResponse({"error": f"Form name cannot be empty at row {idx}."}, status=400)
            
            name_lower = name.lower()
            if name_lower in seen_names:
                return JsonResponse({"error": f"Duplicate form name '{name}' found in payload."}, status=400)
            seen_names.add(name_lower)
            
            # Check DB duplicate
            form_id = item.get("id")
            dup = check_duplicate_form_name(name, form_id)
            if dup:
                return JsonResponse({"error": f"Form name '{name}' already exists in database."}, status=400)

        # Update phase
        for item in items:
            form_id = item.get("id")
            form_name = item.get("form_name").strip()
            status = item.get("status")
            update_form_data_entry(form_id, form_name, status)

        return JsonResponse({"message": "Form Data updated successfully!"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

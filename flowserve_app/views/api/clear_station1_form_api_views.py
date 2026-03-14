from django.http import JsonResponse

from flowserve_app.services.form_service import clear_station1

def clear_station1_form(request):
    clear_station1()
    return JsonResponse({"status":"success"})

from django.http import JsonResponse

from flowserve_app.services.form_service import cancel_station1

def cancel_station1_form(request):
    cancel_station1()
    return JsonResponse({"status":"success"})

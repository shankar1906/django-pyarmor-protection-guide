from django.shortcuts import render
from flowserve_app.decorators import permission_required

@permission_required("Configuration")
def configuration_page(request):
    return render(request, "config2.html")

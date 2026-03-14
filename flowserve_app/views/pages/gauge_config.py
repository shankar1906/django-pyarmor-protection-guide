from django.shortcuts import render, redirect
from flowserve_app.decorators import permission_required

def gauge_config(request):

    return render(request, "gauge_config.html")

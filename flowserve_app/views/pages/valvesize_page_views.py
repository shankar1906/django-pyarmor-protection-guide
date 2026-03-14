from django.shortcuts import render, redirect
from flowserve_app.decorators import permission_required

def valve_size(request):

    return render(request, "valve_size.html")

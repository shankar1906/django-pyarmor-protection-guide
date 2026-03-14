from django.shortcuts import render
from flowserve_app.decorators import permission_required
from flowserve_app.services.pdf_service import get_abrs_value

@permission_required("Graph")
def pdf_report(request):
    get_abrs_value()
    return render(request, "pdf_report.html")

from django.shortcuts import render
from flowserve_app.decorators import permission_required
from flowserve_app.services.form_data_service import get_all_form_data

@permission_required("Form Data")
def form_data_page(request):
    """
    Renders the Form Data management page.
    """
    rows = get_all_form_data()
    form_data = []
    for row in rows:
        form_data.append({
            "id": row[0],
            "form_name": row[1],
            "status": row[2]
        })
    
    return render(request, "form_data.html", {"form_data": form_data})

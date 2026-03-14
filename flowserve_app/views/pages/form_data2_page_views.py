from django.shortcuts import render
from flowserve_app.decorators import permission_required
from flowserve_app.services.form_service import get_valve_type
from flowserve_app.services.form_data2_service import get_enabled_form_data
from flowserve_app.services.valvetype_service import get_all_valve_types

@permission_required("Form Data")
def form_data2_page(request):
    """
    View to render the Form Data 2 page.
    """
    valve_types_data = get_all_valve_types()
    valve_types = valve_types_data.get('valve_types', [])
    form_data_options = get_enabled_form_data()
    
    context = {
        'username': request.session.get('user_name', 'Guest'),
        'valve_types': valve_types,
        'form_data_options': form_data_options
    }
    return render(request, 'form_data2.html', context)

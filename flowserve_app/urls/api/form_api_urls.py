from django.urls import path
from flowserve_app.views.pages.form_page_views import form_page
from flowserve_app.views.api.form_pressure_api_views import get_pressure_duration
from flowserve_app.views.api.save_station1_form_api_views import save_station1_form
from flowserve_app.views.api.clear_station1_form_api_views import clear_station1_form
from flowserve_app.views.api.cancel_station1_form_api_views import cancel_station1_form
from flowserve_app.views.api.continue_station1_api_views import continue_station1
from flowserve_app.views.api.valve_serial_api_views import check_assembly_id, get_assembly_id, save_to_local_db, delete_and_retest_serial


urlpatterns = [
    path("form/", form_page, name="form_page"),
    path("get_pressure_duration/", get_pressure_duration, name="get_pressure_duration"),
    path("save_station1/", save_station1_form, name="save_station1"),
    path("clear_station1/",clear_station1_form,name='clear_station1_form'),
    path("cancel_station1/",cancel_station1_form,name='cancel_station1_form'),
    path("continue_station1/",continue_station1,name='continue_station1'),
    path("check_assembly_id/", check_assembly_id, name="newform_check_assembly_id"),
    path("get_assembly_id/", get_assembly_id, name="newform_get_assembly_id"),
    path("save_to_local_db/", save_to_local_db, name="newform_save_to_local_db"),
    path("delete_and_retest_serial/", delete_and_retest_serial, name="newform_delete_and_retest_serial"),
]

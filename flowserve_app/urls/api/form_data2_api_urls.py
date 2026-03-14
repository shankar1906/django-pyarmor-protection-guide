from django.urls import path
from flowserve_app.views.api.form_data2_api_views import (
    get_form_data2_api,
    save_form_data2_api,
    list_all_configs_api,
    bulk_delete_api,
    delete_valve_type_configs_api
)

urlpatterns = [
    path("formdata2/list/", list_all_configs_api, name="list_all_configs_api"),
    path("formdata2/get/<int:valve_type_id>/", get_form_data2_api, name="get_form_data2_api"),
    path("formdata2/save/", save_form_data2_api, name="save_form_data2_api"),
    path("formdata2/bulk_delete/", bulk_delete_api, name="bulk_delete_api"),
    path("formdata2/delete_valve/<int:valve_type_id>/", delete_valve_type_configs_api, name="delete_valve_type_configs_api"),
]

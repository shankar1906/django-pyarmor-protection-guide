from django.urls import path
from flowserve_app.views.api.form_data_api_views import get_form_data_api, update_form_data_api, delete_form_data_api

urlpatterns = [
    path("formdata/", get_form_data_api, name="api_get_form_data"),
    path("formdata/update/", update_form_data_api, name="api_update_form_data"),
    path("formdata/delete/<int:form_id>/", delete_form_data_api, name="api_delete_form_data"),
]

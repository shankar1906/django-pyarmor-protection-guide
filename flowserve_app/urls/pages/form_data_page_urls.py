from django.urls import path
from flowserve_app.views.pages.form_data_page_views import form_data_page

urlpatterns = [
    path("formdata/", form_data_page, name="form_data"),
]
    
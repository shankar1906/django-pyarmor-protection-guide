from django.urls import path
from flowserve_app.views.pages.form_data2_page_views import form_data2_page

urlpatterns = [
    path("formdata2/", form_data2_page, name="form_data2"),
]

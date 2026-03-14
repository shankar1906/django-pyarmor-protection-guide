from django.urls import path
from flowserve_app.views.pages.form_page_views import form_page

urlpatterns = [
    path("form/", form_page, name="form_page"),
]

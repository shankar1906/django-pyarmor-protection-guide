from django.urls import path
from flowserve_app.views.pages.valve_class_page_views import valve_class_page

urlpatterns = [
    path("valve_class/", valve_class_page, name="valve_class"),
]

from django.urls import path
from flowserve_app.views.pages.configuration_page_views import configuration_page

urlpatterns = [
    path("user_config/", configuration_page, name="configuration"),
]

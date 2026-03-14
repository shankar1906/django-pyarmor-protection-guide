from django.urls import path
from flowserve_app.views.pages.gauge_config import  gauge_config


urlpatterns = [

    path("gauge-config/", gauge_config, name="gauge_config")

]

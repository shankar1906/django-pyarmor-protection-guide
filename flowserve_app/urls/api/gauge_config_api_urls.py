from django.urls import path
from flowserve_app.views.api.gauge_config_api_views import (
    get_gauge_config_api,
    save_gauge_config_api
)

urlpatterns = [
    path("gauge-config/load/", get_gauge_config_api, name="get_gauge_config_api"),
    path("gauge-config/save/", save_gauge_config_api, name="save_gauge_config_api"),
]

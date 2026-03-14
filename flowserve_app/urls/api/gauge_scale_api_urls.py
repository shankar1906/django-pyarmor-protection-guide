"""
URL patterns for Gauge Scale API
"""

from django.urls import path
from flowserve_app.views.api import gauge_scale_api_views

urlpatterns = [
    path('get-gauge-scale/', gauge_scale_api_views.get_gauge_scale_api, name='get_gauge_scale_api'),
    path('get-gauge-scale-from-valve-class/', gauge_scale_api_views.get_gauge_scale_from_valve_class_api, name='get_gauge_scale_from_valve_class_api'),
    path('get-available-options/', gauge_scale_api_views.get_available_options_api, name='get_available_options_api'),
]
from django.urls import path
from flowserve_app.views.pages.regenerate_page_views import regenerate_page
from flowserve_app.views.api.regenerate_api_views import (
    get_serial_numbers,
    get_reports,
    download_pdf
)

urlpatterns = [
    # Page view
    path('regenerate/', regenerate_page, name='regenerate'),
    
    # API endpoints
    path('api/regenerate/serial-numbers/', get_serial_numbers, name='api_regenerate_serial_numbers'),
    path('api/regenerate/reports/', get_reports, name='api_regenerate_reports'),
    path('api/regenerate/download-pdf/', download_pdf, name='api_regenerate_download_pdf'),
]

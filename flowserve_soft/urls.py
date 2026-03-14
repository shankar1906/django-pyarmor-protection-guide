"""
URL configuration for flowserve_soft project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
# from django.urls import path

# urlpatterns = [
#     path('admin/', admin.site.urls),
# ]

from django.urls import path, include
from django.views.generic import RedirectView
from flowserve_app.views.pages.auth_page_views import root_redirect


urlpatterns = [
    # Root URL - redirect to login or dashboard based on auth status
    path("", root_redirect, name="root"),
    
    # Page URLs
    path("", include("flowserve_app.urls.pages.standards_page_urls")),
    path("", include("flowserve_app.urls.pages.valve_class_page_urls")),
    path("", include("flowserve_app.urls.pages.gauge_details_page_urls")),
    path("", include("flowserve_app.urls.pages.instrument_type_page_urls")),
    path("", include("flowserve_app.urls.pages.auth_page_urls")),
    path("shell_material/", include("flowserve_app.urls.pages.shell_material_page_urls")),
    
    path("", include("flowserve_app.urls.pages.gauge_config_page_urls")),
    path("", include("flowserve_app.urls.pages.category_page_urls")),
    path("", include("flowserve_app.urls.pages.valvesize_page_urls")),
    path("", include("flowserve_app.urls.pages.single_live_page_urls")),

    
    # Test Type page urls
    path("", include("flowserve_app.urls.pages.testtype_page_urls")),
    # Test Type page urls
    path("", include("flowserve_app.urls.pages.valvetype_page_urls")),
    # configuration page urls
    path("",include("flowserve_app.urls.pages.configuration_page_urls")),
    
    # form page urls
    path("",include("flowserve_app.urls.pages.form_page_urls")),
    # Form Data page urls
    path("", include("flowserve_app.urls.pages.form_data_page_urls")),
    # Form Data 2 page urls
    path("", include("flowserve_app.urls.pages.form_data2_page_urls")),
    
    # Employee page urls
    path("", include("flowserve_app.urls.pages.employee_page_urls")),
    
    # Alarm page urls
    path("", include("flowserve_app.urls.pages.alarm_page_urls")),
    
    # User Accounting page urls
    path("", include("flowserve_app.urls.pages.user_accounting_page_urls")),
    
    # Graph page urls
    path("", include("flowserve_app.urls.pages.graph_page_urls")),
    
    # vtr page urls
    path("", include("flowserve_app.urls.pages.vtr_page_urls")),
    
    # pdf page urls
    path("", include("flowserve_app.urls.pages.pdf_page_urls")),
    
    # pdf report page urls
    path("",include("flowserve_app.urls.pages.pdf_report_urls")),
    
    # regenerate page urls
    path("", include("flowserve_app.urls.regenerate_urls")),

    # Make default Django login redirect (`/accounts/login/`) go to our custom login page
    path("accounts/login/", RedirectView.as_view(pattern_name="login", permanent=False)),

    # API URLs
    path("api/", include("flowserve_app.urls.api.standards_api_urls")),
    path("api/", include("flowserve_app.urls.api.valve_class_api_urls")),
    path("api/", include("flowserve_app.urls.api.gauge_details_api_urls")),
    path("api/", include("flowserve_app.urls.api.instrument_type_api_urls")),
    path("api/auth/", include("flowserve_app.urls.api.auth_api_urls")),
    path("api/", include("flowserve_app.urls.api.shell_material_api_urls")),
    path("api/", include("flowserve_app.urls.api.gauge_config_api_urls")),
    
    path("api/valve_type/", include("flowserve_app.urls.api.valvetype_api_urls")),
    path("api/testtype/", include("flowserve_app.urls.api.testtype_api_urls")),
    path("api/user_config/", include("flowserve_app.urls.api.configuration_api_urls")),
    path("api/dashboard/", include("flowserve_app.urls.api.testmode_api_urls")),
    path("api/dashboard/", include("flowserve_app.urls.api.newtest_api_urls")),
    path("api/newform/", include("flowserve_app.urls.api.form_api_urls")),
    # Form Data API urls
    path("api/", include("flowserve_app.urls.api.form_data_api_urls")),
    # Form Data 2 API urls
    path("api/", include("flowserve_app.urls.api.form_data2_api_urls")),
    path("api/gauge_scale/", include("flowserve_app.urls.api.gauge_scale_api_urls")),

    path("api/", include("flowserve_app.urls.api.category_api_urls")),
    path("api/", include("flowserve_app.urls.api.valvesize_api_urls")),
    path("api/", include("flowserve_app.urls.api.single_live_page_api_urls")),
    
    # Employee API urls
    path("api/employee/", include("flowserve_app.urls.api.employee_api_urls")),
    
    # Alarm API urls
    path("api/alarm/", include("flowserve_app.urls.api.alarm_api_urls")),
    
    # User Accounting API urls
    path("api/user_accounting/", include("flowserve_app.urls.api.user_accounting_api_urls")),
    
    # Valve Serial API urls
    path("api/newform/", include("flowserve_app.urls.api.valve_serial_api_urls")),
]

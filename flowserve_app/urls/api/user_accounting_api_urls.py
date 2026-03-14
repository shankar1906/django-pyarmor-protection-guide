from django.urls import path
from flowserve_app.views.api.user_accounting_api_views import get_all_user_accounting_api

urlpatterns = [
    path("", get_all_user_accounting_api, name="api_get_all_user_accounting"),
]

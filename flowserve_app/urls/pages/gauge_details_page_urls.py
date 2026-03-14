from django.urls import path
from flowserve_app.views.pages.gauge_details_page_views import gauge_details_page

urlpatterns = [
    path("gauge_details/", gauge_details_page, name="gauge_details"),
]

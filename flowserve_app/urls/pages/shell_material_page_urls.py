from django.urls import path
from flowserve_app.views.pages.shell_material_page_views import shell_material_page

urlpatterns = [
    path("", shell_material_page, name="shell_material"),
]

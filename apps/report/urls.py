from django.urls import path
from apps.report import views

app_name = "report"


urlpatterns = [
    path(
        "create/",
        views.report_create,
        name="create"
    ),

    path(
        "my-reports/",
        views.my_reports,
        name="my_reports"
    ),
    path(
        "delete/<int:id>/",
        views.report_delete,
        name="delete"
    ),
]
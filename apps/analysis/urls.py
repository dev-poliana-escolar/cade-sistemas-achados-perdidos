from django.urls import path
from apps.analysis import views

app_name= 'analysis'

urlpatterns=[
    path(
        "pending_reports/",
        views.pending_reports,
        name="pending_reports"
    ),
    path(
        "pending_deliveries/",
        views.pending_deliveries,
        name="pending_deliveries"
    ),
    path(
        "confirm_delivered/<int:id>/",
        views.confirm_delivered,
        name="confirm_delivered"

    ),
    path(
        "dashboard/",
        views.dashboard,
        name="dashboard"    
    ),
    path(
        "create/<int:id>/",
        views.create_analysis,
        name="create"
    ),
    path(
        "view/<int:reporte_id>/",
        views.view_analysis,
        name="view"
    )

]
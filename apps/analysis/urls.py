from django.urls import path
from apps.analysis import views

app_name= 'analysis'

urlpatterns=[
     path(
        "pending_reports/",
        views.pending_reports,
        name="pending_reports"
    ),

]
from django.urls import path
from apps.items import api_views
from apps.items import views


app_name = "items"


urlpatterns = [

    path(
        "",
        views.found_items,
        name="found_items"
    ),

    path(
        "donations/",
        views.donation_items,
        name="donation_items"
    ),

    path(
        "my-items/",
        views.my_items,
        name="my_items"
    ),

    path(
        "admin-items/",
        views.admin_items,
        name="admin_items"
    ),

    path(
        "create/",
        views.item_create,
        name="create"
    ),

    path(
        "<int:pk>/edit/",
        views.item_edit,
        name="edit"
    ),

    path(
        "<int:pk>/cancel/",
        views.item_cancel,
        name="cancel"
    ),

    path(
        "<int:pk>/delete/",
        views.item_delete,
        name="delete"
    ),

    path(
        "api/<int:pk>/",
        api_views.api_item_detail,
        name="api_item_detail"
    ),
]
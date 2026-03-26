from django.urls import path

from . import views

urlpatterns = [
    path("", views.events_page, name="events-page"),
    path("manage/", views.manage_page, name="events-manage-page"),
    path("events/<int:event_id>/", views.event_detail_page, name="event-detail-page"),
]

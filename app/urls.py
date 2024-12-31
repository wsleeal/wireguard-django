from django.urls import path
from app import views


urlpatterns = [
    path("download-peer-conf/<int:id>/", views.download_peer_conf, name="download-peer-conf"),
    path("populate-peer-status/", views.populate_peer_status, name="populate-peer-status"),
]

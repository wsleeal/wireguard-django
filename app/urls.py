from django.urls import path
from app import views


urlpatterns = [
    path("download-peer-conf/<int:id>/", views.download_peer_conf, name="download-peer-conf"),
    path("index/", views.index, name="index"),
]

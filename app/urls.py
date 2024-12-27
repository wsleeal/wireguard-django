from django.urls import path
from app import views


urlpatterns = [
    path("index/<int:id>/", views.index, name="index"),
]

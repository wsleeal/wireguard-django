from django.contrib import admin
from app import models


@admin.register(models.Server)
class ServerAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Peer)
class PeerAdmin(admin.ModelAdmin):
    readonly_fields = ("address",)

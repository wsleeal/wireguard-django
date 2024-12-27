from django.contrib import admin
from app import models


@admin.register(models.Server)
class ServerAdmin(admin.ModelAdmin):
    readonly_fields = ("private_key", "public_key")


@admin.register(models.Peer)
class PeerAdmin(admin.ModelAdmin):
    readonly_fields = ("private_key", "public_key", "address", "preshared_key")

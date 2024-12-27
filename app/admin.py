from django.contrib import admin
from app import models


@admin.register(models.Server)
class ServerAdmin(admin.ModelAdmin):
    readonly_fields = ("file", "file_md5")


@admin.register(models.Peer)
class PeerAdmin(admin.ModelAdmin):
    pass

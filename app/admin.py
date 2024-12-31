from django.contrib import admin
from app import models


@admin.register(models.Server)
class ServerAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "listen_port", "endpoint", "persistent_keepalive", "dst_host")


@admin.register(models.Peer)
class PeerAdmin(admin.ModelAdmin):
    list_display = ("name", "server", "address", "allowed_ips")
    readonly_fields = ("address",)
    change_form_template = "custom_admin/change_form.html"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "server":
            if db_field.blank:
                kwargs["queryset"] = models.Server.objects.filter(name="123")

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = (
            "js/custom_admin.js",
            "https://cdn.rawgit.com/davidshimjs/qrcodejs/gh-pages/qrcode.min.js",
        )
        css = {
            "all": ("css/custom_admin.css",),
        }


@admin.register(models.PeerStatus)
class PeerStatusAdmin(admin.ModelAdmin):
    list_display = ("peer", "endpoint", "last_handshake", "tx", "rx")

    def get_readonly_fields(self, request, obj=None):
        return self.list_display

from django.contrib import admin
from app.models import Server, Peer, PeerStatus, PeerStatusUnit
from django.utils import timezone


@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "address", "listen_port", "endpoint", "persistent_keepalive")


@admin.register(Peer)
class PeerAdmin(admin.ModelAdmin):
    list_display = ("name", "server", "address", "allowed_ips")
    readonly_fields = ("address",)
    change_form_template = "custom_admin/change_form.html"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "server":
            if db_field.blank:
                kwargs["queryset"] = Server.objects.filter(name="123")

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = (
            "js/custom_admin.js",
            "https://cdn.rawgit.com/davidshimjs/qrcodejs/gh-pages/qrcode.min.js",
        )
        css = {
            "all": ("css/custom_admin.css",),
        }


@admin.register(PeerStatus)
class PeerStatusAdmin(admin.ModelAdmin):
    list_display = ("peer", "online", "last_handshake", "tx", "rx")
    readonly_fields = ("peer", "online", "last_handshake", "tx", "rx")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_last_status(self, peer_public_key: str):
        """
        Retorna o último registro de PeerStatusUnit para a chave pública fornecida.
        """
        return PeerStatusUnit.objects.filter(public_key=peer_public_key).last()

    @admin.display(boolean=True, description="Online")
    def online(self, obj: PeerStatus):
        status = self.get_last_status(obj.peer.public_key)
        if status:
            diff = timezone.now() - status.last_handshake
            return diff.total_seconds() < 120
        return None

    def last_handshake(self, obj: PeerStatus):
        last_status = self.get_last_status(obj.peer.public_key)
        return last_status.last_handshake if last_status else None

    def tx(self, obj: PeerStatus):
        last_status = self.get_last_status(obj.peer.public_key)
        return last_status.tx if last_status else None

    def rx(self, obj: PeerStatus):
        last_status = self.get_last_status(obj.peer.public_key)
        return last_status.rx if last_status else None

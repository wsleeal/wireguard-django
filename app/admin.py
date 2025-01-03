from django.contrib import admin
from app.models import Server, Peer, PeerStatus, PeerStatusUnit


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

    def get_peer_status_units(self, peer_public_key: str):
        """
        Retorna os dois últimos registros de PeerStatusUnit para a chave pública fornecida.
        """
        return PeerStatusUnit.objects.filter(public_key=peer_public_key).order_by("-created_at")[:2]

    @admin.display(boolean=True, description="Online")
    def online(self, obj: PeerStatus):
        last_two_status = self.get_peer_status_units(obj.peer.public_key)
        if not last_two_status.exists():
            return None

        if last_two_status.count() == 1:
            rx_new = int(last_two_status[0].rx)
            rx_old = 0
        else:
            rx_new = int(last_two_status[0].rx)
            rx_old = int(last_two_status[1].rx)

        return rx_new > rx_old

    def get_last_status(self, peer_public_key: str):
        """
        Retorna o último registro de PeerStatusUnit para a chave pública fornecida.
        """
        return PeerStatusUnit.objects.filter(public_key=peer_public_key).last()

    def last_handshake(self, obj: PeerStatus):
        last_status = self.get_last_status(obj.peer.public_key)
        return last_status.last_handshake if last_status else None

    def tx(self, obj: PeerStatus):
        last_status = self.get_last_status(obj.peer.public_key)
        return last_status.tx if last_status else None

    def rx(self, obj: PeerStatus):
        last_status = self.get_last_status(obj.peer.public_key)
        return last_status.rx if last_status else None

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

    @admin.display(boolean=True, description="Online")
    def online(self, obj: PeerStatus):

        last_two_status = PeerStatusUnit.objects.filter(public_key=obj.peer.public_key).order_by("-created_at")[:2]
        count = last_two_status.count()

        if count == 0:
            return None

        if count > 0 and count < 2:
            status_new = last_two_status.get()
            rx_new, rx_old = int(status_new.rx), 0
        else:
            status_new, status_old = last_two_status
            rx_new, rx_old = int(status_new.rx), int(status_old.rx)

        if sum([rx_new, rx_old]) and rx_new > rx_old:
            return True
        return False

    def last_handshake(self, obj: PeerStatus):
        last_status = PeerStatusUnit.objects.filter(public_key=obj.peer.public_key).last()
        return last_status.last_handshake

    def tx(self, obj: PeerStatus):
        last_status = PeerStatusUnit.objects.filter(public_key=obj.peer.public_key).last()
        return last_status.tx

    def rx(self, obj: PeerStatus):
        last_status = PeerStatusUnit.objects.filter(public_key=obj.peer.public_key).last()
        return last_status.rx

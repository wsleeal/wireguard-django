from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from django.core.validators import validate_ipv4_address
from django.core.files.storage import FileSystemStorage
from django.dispatch import receiver
from django.db.models import OuterRef, Subquery
from django.db.models import Q
from django.db import models
from app.utils import wg_tools
import os


class BaseModel(models.Model):
    class Meta:
        abstract = True

    private_key = models.CharField(max_length=44, default=wg_tools.generate_private_key, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def public_key(self):
        return wg_tools.generate_public_key(self.private_key)


class WireguardStorage(FileSystemStorage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._location = "/etc/wireguard"
        self._file_permissions_mode = 0o600

    def get_available_name(self, name, max_length=None):
        file_path = os.path.join(self.location, name)
        if os.path.exists(file_path):
            os.remove(file_path)
        return name


class Server(BaseModel):
    class Meta:
        verbose_name = "Server"
        verbose_name_plural = "Servers"
        ordering = ["id"]

    name = models.CharField(max_length=100)
    address = models.GenericIPAddressField(protocol="ipv4", unique=True, validators=(validate_ipv4_address,))
    listen_port = models.SmallIntegerField(default=51820, unique=True)
    endpoint = models.GenericIPAddressField(protocol="ipv4", validators=(validate_ipv4_address,))
    persistent_keepalive = models.SmallIntegerField(default=25)
    file = models.FileField(storage=WireguardStorage(), null=True, editable=False)
    file_md5 = models.CharField(max_length=255, null=True, editable=False)

    def __str__(self):
        return self.name


class Peer(BaseModel):

    class Meta:
        verbose_name = "Peer"
        verbose_name_plural = "Peers"
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(fields=["server"], condition=Q(central=True), name="unique_central_peer_per_server"),
        ]

    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address = models.GenericIPAddressField(protocol="ipv4", unique=True, editable=False, validators=(validate_ipv4_address,))
    preshared_key = models.CharField(max_length=44, editable=False, default=wg_tools.generate_preshared_key)
    allowed_ips = models.CharField(max_length=255, null=True, blank=True)
    central = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class PeerStatus(models.Model):
    class Meta:
        verbose_name = "Status"
        verbose_name_plural = "Status"
        ordering = ["id"]

    peer = models.OneToOneField(Peer, on_delete=models.CASCADE, editable=False)


class PeerStatusUnit(models.Model):
    server_name = models.CharField(max_length=255)
    public_key = models.CharField(max_length=255)
    preshared_key = models.CharField(max_length=255)
    endpoint = models.CharField(max_length=255)
    allowed_hosts = models.CharField(max_length=255)
    last_handshake = models.DateTimeField()
    tx = models.CharField(max_length=255)
    rx = models.CharField(max_length=255)
    keepaline = models.SmallIntegerField(default=25)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def keep_only_two_recent(cls):
        """
        Mantém apenas os dois registros mais recentes para cada public_key e exclui os demais.
        """
        # Subconsulta para obter os IDs dos dois mais recentes para cada public_key
        recent_ids = cls.objects.filter(public_key=OuterRef("public_key")).order_by("-created_at").values("id")[:2]

        # Obtém os IDs a serem mantidos
        ids_to_keep = cls.objects.filter(id__in=Subquery(recent_ids)).values_list("id", flat=True)

        # Exclui os registros que não estão nos IDs a serem mantidos
        cls.objects.exclude(id__in=ids_to_keep).delete()


@receiver(pre_save, sender=Peer)
def add_peer_ip(sender, instance: Peer, **kwargs):
    if not instance.created_at:
        instance.address = wg_tools.find_next_available_ip(instance.server)


@receiver(post_save, sender=Server)
def reload_server_interface(sender, instance: Server, **kwargs):
    wg_tools.generate_wg_conf_file(server=instance)
    wg_tools.down_wg_interface(server=instance)
    wg_tools.up_wg_interface(server=instance)


@receiver(post_delete, sender=Server)
def delete_server_conf(sender, instance: Server, **kwargs):
    wg_tools.down_wg_interface(server=instance)
    instance.file.delete(save=False)


@receiver(post_save, sender=Peer)
def reload_peer_interface(sender, instance: Peer, **kwargs):
    instance.server.save()


@receiver(post_delete, sender=Peer)
def delete_peer_conf(sender, instance: Peer, **kwargs):
    instance.server.save()

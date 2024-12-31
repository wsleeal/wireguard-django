from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from django.core.validators import validate_ipv4_address
from django.core.files.storage import FileSystemStorage
from django.dispatch import receiver
from django.db import models
from app.utils import wg_tools


class BaseModel(models.Model):
    class Meta:
        abstract = True

    private_key = models.CharField(max_length=44, default=wg_tools.generate_private_key, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def public_key(self):
        return wg_tools.generate_public_key(self.private_key)


fs = FileSystemStorage(location="/etc/wireguard", file_permissions_mode=0o600)


def file_upload_path(instance: "Server", filename: str):
    # Define o nome fixo do arquivo
    return f"{instance.id}.conf"


class Server(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    address = models.GenericIPAddressField(protocol="ipv4", unique=True, validators=(validate_ipv4_address,))
    listen_port = models.SmallIntegerField(default=51820, unique=True)
    endpoint = models.GenericIPAddressField(protocol="ipv4", validators=(validate_ipv4_address,))
    persistent_keepalive = models.SmallIntegerField(default=25)
    file = models.FileField(storage=fs, upload_to=file_upload_path, null=True, editable=False)
    file_md5 = models.CharField(max_length=255, null=True, editable=False)

    def __str__(self):
        return self.name


class Peer(BaseModel):
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)
    address = models.GenericIPAddressField(protocol="ipv4", unique=True, editable=False, validators=(validate_ipv4_address,))
    preshared_key = models.CharField(max_length=44, editable=False, default=wg_tools.generate_preshared_key)
    allowed_ips = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


class PeerStatus(models.Model):
    peer = models.ForeignKey(Peer, on_delete=models.CASCADE)
    endpoint = models.CharField(max_length=50)
    last_handshake = models.DateTimeField()
    tx = models.CharField(max_length=255)
    rx = models.CharField(max_length=255)


@receiver(pre_save, sender=Peer)
def add_peer_ip(sender, instance: Peer, **kwargs):
    if not instance.created_at:
        instance.address = wg_tools.find_next_available_ip(instance.server)


@receiver(post_save, sender=Server)
def update_conf_from_server(sender, instance: Server, **kwargs):
    wg_tools.generate_wg_conf_file(server=instance)
    wg_tools.up_wg_interface(server=instance)


@receiver(post_save, sender=Peer)
def update_conf_from_peer(sender, instance: Peer, **kwargs):
    wg_tools.generate_wg_conf_file(server=instance.server)
    wg_tools.up_wg_interface(server=instance.server)


@receiver(post_delete, sender=Server)
def delete_server_conf(sender, instance: Server, **kwargs):
    wg_tools.down_wg_interface(server=instance)
    instance.file.delete(save=False)


@receiver(post_delete, sender=Peer)
def delete_peer_conf(sender, instance: Server, **kwargs):
    wg_tools.generate_wg_conf_file(server=instance.server)
    wg_tools.up_wg_interface(server=instance.server)

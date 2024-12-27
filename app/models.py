from django.core.validators import validate_ipv4_address
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.db import models
from nacl.public import PrivateKey
from nacl.encoding import Base64Encoder


import os
import base64


def generate_wg_psk():
    psk_bytes = os.urandom(32)
    psk_base64 = base64.b64encode(psk_bytes).decode("utf-8")
    return psk_base64


def get_next_ip(server: "Server"):
    address = server.address
    last_peer = Peer.objects.filter(server=server).last()
    if last_peer:
        address = last_peer.address

    parts = address.split(".")
    parts[-1] = str(int(parts[-1]) + 1)
    next_ip = ".".join(parts)
    return next_ip


def generate_keys():
    private = PrivateKey.generate()
    public = private.public_key

    private_utf8 = private.encode(Base64Encoder).decode()
    public_utf8 = public.encode(Base64Encoder).decode()

    return private_utf8, public_utf8


class Server(models.Model):
    name = models.CharField(max_length=100)
    address = models.GenericIPAddressField(protocol="ipv4", validators=(validate_ipv4_address,))
    listen_port = models.SmallIntegerField(default=51820)
    private_key = models.CharField(max_length=44, editable=False)
    public_key = models.CharField(max_length=44, editable=False)
    endpoint = models.GenericIPAddressField(protocol="ipv4", validators=(validate_ipv4_address,))
    persistent_keepalive = models.SmallIntegerField(default=25)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Peer(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address = models.GenericIPAddressField(protocol="ipv4", editable=False, validators=(validate_ipv4_address,))
    private_key = models.CharField(max_length=44, editable=False)
    public_key = models.CharField(max_length=44, editable=False)
    preshared_key = models.CharField(max_length=44, editable=False, default=generate_wg_psk)
    allowed_ips = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


@receiver(pre_save, sender=Server)
def add_server_keys(sender, instance: Server, **kwargs):
    if not instance.created_at:
        instance.private_key, instance.public_key = generate_keys()


@receiver(pre_save, sender=Peer)
def ad_peer_keys(sender, instance: Peer, **kwargs):
    if not instance.created_at:
        instance.private_key, instance.public_key = generate_keys()
        instance.address = get_next_ip(instance.server)


@receiver(post_save, sender=Server)
def update_conf_from_server(sender, instance: Server, **kwargs):
    from app.utils import wg_tools

    wg_tools.generate_wg_conf(server=instance)


@receiver(post_save, sender=Peer)
def update_conf_from_peer(sender, instance: Peer, **kwargs):
    from app.utils import wg_tools

    wg_tools.generate_wg_conf(server=instance.server)

from nacl.public import PrivateKey
from nacl.encoding import Base64Encoder
import subprocess
import os


try:
    from app.models import Server, Peer
except:
    pass


def generate_wg_conf_content(server: "Server"):

    from app.models import Peer

    config_lines = [
        "[Interface]",
        f"# server: {server.name}",
        f"# endpoint: {server.endpoint}",
        f"Address = {server.address}",
        f"ListenPort = {server.listen_port}",
        f"PrivateKey = {server.private_key}",
        r"PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -A FORWARD -o %i -j ACCEPT",
        r"PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -D FORWARD -o %i -j ACCEPT",
        "",
    ]

    for peer in Peer.objects.filter(server=server).all():

        allowed_ips = peer.address + "/32"
        if peer.allowed_ips:
            allowed_ips += f", {peer.allowed_ips}"

        config_lines.append("[Peer]")
        config_lines.append(f"# peer: {peer.name}")
        config_lines.append(f"PublicKey = {peer.public_key}")
        config_lines.append(f"PresharedKey = {peer.preshared_key}")
        config_lines.append(f"AllowedIPs = {allowed_ips}")
        config_lines.append(f"PersistentKeepalive = {server.persistent_keepalive}")
        config_lines.append("")

    config_content = "\n".join(config_lines)

    return config_content


def generate_peer_conf_content(peer: "Peer") -> str:

    from app.models import Peer

    allowed_ips = set()

    neighbors = Peer.objects.filter(server=peer.server).exclude(pk=peer.pk)

    for neighbor in neighbors:
        if neighbor.allowed_ips:
            for cidr in neighbor.allowed_ips.split(","):
                allowed_ips.add(cidr.strip())

    if peer.server.dst_host and peer.server.dst_host.allowed_ips:
        allowed_ips.clear()
        for cidr in peer.server.dst_host.allowed_ips.split(","):
            if peer.pk != peer.server.pk:
                allowed_ips.add(cidr.strip())

    allowed_ips.add(f"{peer.server.address}/32")
    allowed_ips.add(f"{peer.address}/32")

    config_lines = [
        "[Interface]",
        f"Address = {peer.address}",
        f"PrivateKey = {peer.private_key}",
        "ListenPort = 51820",
        "",
        "[Peer]",
        f"PublicKey = {peer.server.public_key}",
        f"PresharedKey = {peer.preshared_key}",
        f"Endpoint = {peer.server.endpoint}:{peer.server.listen_port}",
        f"AllowedIPs = {", ".join(allowed_ips)}",
        f"PersistentKeepalive = {peer.server.persistent_keepalive}",
        "",
    ]

    config_content = "\n".join(config_lines)

    return config_content


def generate_wg_conf_file(server: "Server"):

    from django.core.files import File
    from io import BytesIO
    import hashlib

    if not server.id:
        return

    content = generate_wg_conf_content(server)
    content_md5 = hashlib.md5(content.encode()).hexdigest()

    if server.file:
        if os.path.exists(server.file.path):
            if server.file_md5 == content_md5:
                return

    file_content = BytesIO(content.encode())
    server.file = File(file_content, name=f"{server.id}.conf")
    server.file_md5 = content_md5
    server.save()


def up_wg_interface(server: "Server"):
    if server.file:
        subprocess.run(["wg-quick", "up", server.file.path], check=True)


def down_wg_interface(server: "Server"):
    result = subprocess.run(["wg", "show", "interfaces"], capture_output=True, text=True, check=True)
    interfaces = result.stdout.split()
    for interface in interfaces:
        if interface == str(server.id):
            subprocess.run(["wg-quick", "down", interface], check=True)


def generate_private_key() -> str:
    private_key = PrivateKey.generate()
    private_key_base64 = private_key.encode(Base64Encoder).decode("utf-8")
    return private_key_base64


def generate_public_key(private_key_base64: str):
    decoded_private_key = PrivateKey(Base64Encoder.decode(private_key_base64.encode()))
    public_key = decoded_private_key.public_key
    public_key_base64 = public_key.encode(Base64Encoder).decode("utf-8")
    return public_key_base64


def generate_preshared_key():
    preshared_key = os.urandom(32)
    preshared_key_base64 = Base64Encoder.encode(preshared_key).decode()
    return preshared_key_base64


def find_next_available_ip(server: "Server"):
    from app.models import Peer

    address = server.address
    last_peer = Peer.objects.filter(server=server).last()

    if last_peer:
        address = last_peer.address

    parts = address.split(".")
    parts[-1] = str(int(parts[-1]) + 1)
    next_ip = ".".join(parts)

    return next_ip

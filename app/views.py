from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse, HttpResponse
from app.models import Server, Peer
from django.conf import settings
import subprocess
import os


def generate_wg_conf(server: Server):

    config_lines = [
        "[Interface]",
        f"Address = {server.address}",
        f"ListenPort = {server.listen_port}",
        f"PrivateKey = {server.private_key}",
        r"PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -A FORWARD -o %i -j ACCEPT",
        r"PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -D FORWARD -o %i -j ACCEPT",
        "",
    ]

    for peer in Peer.objects.filter(server=server):

        allowed_ips = peer.address + "/32"
        if peer.allowed_ips:
            allowed_ips += f", {peer.allowed_ips}"

        config_lines.append("[Peer]")
        config_lines.append(f"# peer: {peer.name}")
        config_lines.append(f"PublicKey = {peer.public_key}")
        config_lines.append(f"PresharedKey = {peer.preshared_key}")
        config_lines.append(f"AllowedIPs = {allowed_ips}")
        config_lines.append("")

    config_content = "\n".join(config_lines)

    config_dir = os.path.join(settings.BASE_DIR, "wg_configs")
    os.makedirs(config_dir, exist_ok=True)

    file_path = os.path.join(config_dir, "wg0.conf")

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(config_content)

    try:
        subprocess.check_output("wg-quick down wg0", shell=True, text=True)
    except:
        pass

    try:
        subprocess.check_output("wg-quick up wg0", shell=True, text=True)
    except:
        pass


def generate_peer_conf(peer: Peer) -> str:

    allowed_ips = set()

    allowed_ips.add(f"{peer.server.address}/32")

    for neighbor in Peer.objects.filter(server=peer.server).all():

        if neighbor.pk == peer.pk:
            continue

        if not neighbor.allowed_ips:
            continue

        for cidr in neighbor.allowed_ips.split(","):
            allowed_ips.add(cidr.strip())

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


def index(request: WSGIRequest):

    servers = Server.objects.all()

    if not servers.count():
        return JsonResponse({"status": "no servers"})

    for server in servers:
        generate_wg_conf(server)

    return JsonResponse({"status": "OK"})


def index2(request: WSGIRequest):

    peer = Peer.objects.last()

    # Gerando o conteúdo do arquivo
    config_content = generate_peer_conf(peer)

    # Criando uma resposta HTTP com o conteúdo do arquivo
    response = HttpResponse(config_content, content_type="text/plain")

    # Definindo o nome do arquivo para download
    response["Content-Disposition"] = f'attachment; filename="{peer.name}.conf"'

    return response

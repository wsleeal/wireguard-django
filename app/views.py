from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from app.models import Peer, PeerStatus
from app.utils import wg_tools
from django.contrib.auth.decorators import login_required
import subprocess
from datetime import datetime


@login_required
def download_peer_conf(request: WSGIRequest, id: int):
    peer = get_object_or_404(Peer, id=id)
    config_content = wg_tools.generate_peer_conf_content(peer)
    response = HttpResponse(config_content, content_type="text/plain")
    response["Content-Disposition"] = 'attachment; filename="peer.conf"'

    return response


class Status:
    def __init__(self, status: list):
        self.server_name = status[0]
        self.public_key = status[1]
        self.preshared_key = status[2]
        self.endpoint = status[3]
        self.allowed_hosts = status[4]
        self.last_handshake = status[5]
        self.tx = status[6]
        self.rx = status[7]
        self.keepaline = status[8]

    def defaults(self, peer: Peer):
        return {
            "peer_id": peer.id,
            "endpoint": self.endpoint,
            "last_handshake": datetime.fromtimestamp(int(self.last_handshake)),
            "tx": self.tx,
            "rx": self.rx,
        }


def populate_peer_status(request: WSGIRequest):
    result = subprocess.run(["wg", "show", "all", "dump"], capture_output=True, text=True, check=True)
    peer_status: list[Status] = list()
    for line in result.stdout.split("\n"):
        column = line.split()
        if len(column) == 9:
            peer_status.append(Status(column))

    for peer in Peer.objects.all():
        for status in peer_status:
            if status.public_key == peer.public_key:
                PeerStatus.objects.update_or_create(defaults=status.defaults(peer), id=peer.id)

    return HttpResponse()

from django.core.management.base import BaseCommand
from app.models import Peer, PeerStatus
from datetime import datetime
from zoneinfo import ZoneInfo
import subprocess
from app.utils import wg_tools


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
            "last_handshake": datetime.fromtimestamp(int(self.last_handshake), tz=ZoneInfo("America/Sao_Paulo")),
            "tx": self.tx,
            "rx": self.rx,
        }


class Command(BaseCommand):
    help = "Atualiza status do peers"

    @wg_tools.subprocess_logger
    def handle(self, *args, **kwargs):
        result = subprocess.check_output(["wg", "show", "all", "dump"], stderr=subprocess.PIPE, text=True)
        peer_status: list[Status] = list()
        for line in result.split("\n"):
            column = line.split()
            if len(column) == 9:
                peer_status.append(Status(column))

        for peer in Peer.objects.all():
            for status in peer_status:
                if status.public_key == peer.public_key:
                    PeerStatus.objects.update_or_create(defaults=status.defaults(peer), id=peer.id)

        wg_tools.logger.debug("Peers atualizados!")

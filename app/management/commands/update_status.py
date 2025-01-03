from django.core.management.base import BaseCommand
from datetime import datetime
from zoneinfo import ZoneInfo
import subprocess
from app.utils import wg_tools
from app.models import PeerStatusUnit, PeerStatus, Peer


def status_dict(status):
    return {
        "server_name": status[0],
        "public_key": status[1],
        "preshared_key": status[2],
        "endpoint": status[3],
        "allowed_hosts": status[4],
        "last_handshake": datetime.fromtimestamp(int(status[5]), tz=ZoneInfo("America/Sao_Paulo")),
        "tx": status[6],
        "rx": status[7],
        "keepaline": status[8],
    }


class Command(BaseCommand):
    help = "Atualiza status do peers"

    @wg_tools.subprocess_logger
    def handle(self, *args, **kwargs):
        result = subprocess.check_output(["wg", "show", "all", "dump"], stderr=subprocess.PIPE, text=True)
        for line in result.split("\n"):
            column = line.split()
            if len(column) == 9:
                PeerStatusUnit.objects.create(**status_dict(column))

        wg_tools.logger.debug("Peers atualizados!")

        peers = Peer.objects.all()
        if peers.count():
            for peer in peers.all():
                PeerStatus.objects.update_or_create(peer_id=peer.id, defaults={})

        PeerStatusUnit.keep_only_two_recent()

from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from app.models import Peer
from app.utils import wg_tools
from django.contrib.auth.decorators import login_required


@login_required
def download_peer_conf(request: WSGIRequest, id: int):
    peer = get_object_or_404(Peer, id=id)
    config_content = wg_tools.generate_peer_conf_content(peer)
    response = HttpResponse(config_content, content_type="text/plain")
    response["Content-Disposition"] = 'attachment; filename="peer.conf"'

    return response

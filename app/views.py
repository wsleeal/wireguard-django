from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from app.models import Peer
from app.utils import wg_tools
from django.contrib.auth.decorators import login_required


@login_required
def download_peer_conf(request: WSGIRequest, id: int):

    peer = get_object_or_404(Peer, id=id)

    # Gerando o conteúdo do arquivo
    config_content = wg_tools.generate_peer_conf_content(peer)

    # Criando uma resposta HTTP com o conteúdo do arquivo
    response = HttpResponse(config_content, content_type="text/plain")

    # Definindo o nome do arquivo para download
    response["Content-Disposition"] = f'attachment; filename="{peer.name}.conf"'

    return response

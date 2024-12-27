from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse, HttpResponse
from app.models import Server, Peer
from app.utils import wg_tools


def index(request: WSGIRequest):

    peer = Peer.objects.last()

    # Gerando o conteúdo do arquivo
    config_content = wg_tools.generate_peer_conf_content(peer)

    # Criando uma resposta HTTP com o conteúdo do arquivo
    response = HttpResponse(config_content, content_type="text/plain")

    # Definindo o nome do arquivo para download
    response["Content-Disposition"] = f'attachment; filename="{peer.name}.conf"'

    return response

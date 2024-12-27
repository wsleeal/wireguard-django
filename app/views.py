from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse, HttpResponse
from app.models import Server, Peer
from app.utils import wg_tools


def index(request: WSGIRequest):

    servers = Server.objects.all()

    if not servers.count():
        return JsonResponse({"status": "no servers"})

    for server in servers:
        wg_tools.generate_wg_conf(server)

    return JsonResponse({"status": "OK"})


def index2(request: WSGIRequest):

    peer = Peer.objects.last()

    # Gerando o conteúdo do arquivo
    config_content = wg_tools.generate_peer_conf(peer)

    # Criando uma resposta HTTP com o conteúdo do arquivo
    response = HttpResponse(config_content, content_type="text/plain")

    # Definindo o nome do arquivo para download
    response["Content-Disposition"] = f'attachment; filename="{peer.name}.conf"'

    return response


# from django.conf import settings
# from django.http import HttpResponseForbidden


# def internal_only_view(request):
#     # Verifica se a chave secreta está presente nos cabeçalhos
#     if request.META.get("HTTP_X_DJANGO_INTERNAL_KEY") != settings.DJANGO_INTERNAL_KEY:
#         return HttpResponseForbidden("Access forbidden")

#     return HttpResponse("Access granted from internal source.")


# from django.test import Client
# from django.conf import settings


# def my_signal_handler(sender, instance, **kwargs):
#     client = Client()
#     response = client.get("/internal-only/", HTTP_X_DJANGO_INTERNAL_KEY=settings.DJANGO_INTERNAL_KEY)
#     print(response.content)

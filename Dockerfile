# Usar a imagem oficial do Python com Alpine para um contêiner pequeno e rápido
FROM python:3.13.1-alpine3.21

# Atualizar os pacotes e instalar dependências necessárias em uma única camada
RUN apk update && apk upgrade && apk add --no-cache \
    wireguard-tools \
    iproute2 \
    iptables \
    iputils \
    cronie

# Variáveis de ambiente para otimizar o comportamento do Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Criar e ativar um ambiente virtual
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Definir o diretório de trabalho para o código
WORKDIR /code

# Copiar somente os arquivos necessários para a imagem em fases específicas
COPY requirements.txt .

# Instalar as dependências do projeto
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar o código do projeto para o contêiner
COPY . .

# Criar diretório para WireGuard
RUN mkdir -p /etc/wireguard

# Criar diretório para SQLite
RUN mkdir -p /code/database

# Criar diretório para Backup
RUN mkdir -p /code/backup

# Criar o diretório de logs e garantir permissões
RUN mkdir -p /code/log

# Copiar o script de entrypoint e garantir permissões
COPY script/entrypoint.sh /
RUN chmod +x /entrypoint.sh

# CRON Jobs
RUN echo "* * * * * /opt/venv/bin/python /code/manage.py update_status" > /etc/crontabs/root
RUN echo "0 0 * * * sh /code/script/backup.sh" >> /etc/crontabs/root

# Definir o script de entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Expor as portas do aplicativo e WireGuard
EXPOSE 8000 51820/udp

# Comando padrão para rodar o servidor Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

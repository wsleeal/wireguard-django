#!/bin/sh

python manage.py migrate

WIREGUARD_PATH="/etc/wireguard/"

if [ -d "$WIREGUARD_PATH" ]; then
  for arquivo in "$WIREGUARD_PATH"*; do
    if [ -f "$arquivo" ]; then
      wg-quick up "$arquivo"
    fi
  done
fi

exec "$@"

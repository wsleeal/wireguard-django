#!/bin/sh

WIREGUARD_PATH="/etc/wireguard/"

if [ -d "$WIREGUARD_PATH" ]; then
  chmod 600 "$WIREGUARD_PATH"*
  
  for arquivo in "$WIREGUARD_PATH"*; do
    if [ -f "$arquivo" ]; then
      wg-quick up "$arquivo"
    fi
  done
fi

exec "$@"

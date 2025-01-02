#!/bin/sh

# chmod +x /code/backup.sh
/opt/venv/bin/python /code/manage.py dumpdata > /code/backup/backup_$(date +%Y_%m_%d).json

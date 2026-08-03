#!/bin/bash
cd /opt/estudo_musica
source .venv/bin/activate
set -a
source .env
set +a
exec gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 30 run:app

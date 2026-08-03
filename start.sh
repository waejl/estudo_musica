#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${VENV_DIR:-$ROOT_DIR/.venv}"
ENV_FILE="${ENV_FILE:-$ROOT_DIR/.env}"
RUN_AUTO_SETUP="${RUN_AUTO_SETUP:-true}"

cd "$ROOT_DIR"

if [ ! -f "$ENV_FILE" ]; then
    echo "Arquivo .env não encontrado em: $ENV_FILE"
    echo "Crie o .env com DATABASE_URL apontando para o Postgres instalado na máquina."
    exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "Criando venv em $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

echo "Atualizando pip e instalando dependências..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-5000}"
WORKERS="${WORKERS:-2}"

echo "Validando configuração do banco..."
python - <<'PY'
import os
import sys
from sqlalchemy import create_engine, text

database_url = os.environ.get("DATABASE_URL")
if not database_url:
    print("DATABASE_URL não configurado no .env.", file=sys.stderr)
    sys.exit(1)

engine = create_engine(database_url)
with engine.connect() as conn:
    conn.execute(text("SELECT 1"))
print("Conexão com banco validada.")
PY

export FLASK_APP=run.py
if [ "$RUN_AUTO_SETUP" = "true" ]; then
    echo "Garantindo tabelas e dados padrão (flask auto-setup)..."
    flask auto-setup
else
    echo "auto-setup ignorado porque RUN_AUTO_SETUP=$RUN_AUTO_SETUP."
fi

echo "Iniciando com Gunicorn em $HOST:$PORT..."
exec gunicorn --bind "$HOST:$PORT" --workers "$WORKERS" --timeout 30 run:app

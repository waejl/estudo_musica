#!/bin/bash
#
# Script para configurar e iniciar o ambiente de desenvolvimento localmente.
#
# REQUISITOS:
#   - Python 3.12 ou superior
#   - PostgreSQL instalado e rodando localmente.
#   - Um banco de dados e um usuário criados no PostgreSQL.
#
# COMO USAR:
#   1. Dê permissão de execução ao script:
#      chmod +x setup_local.sh
#   2. Execute o script:
#      ./setup_local.sh
#

set -e # Encerra o script se algum comando falhar

VENV_DIR=".venv"
PYTHON_EXEC="python3.12" # Mude se seu executável do Python tiver um nome diferente

echo "=== Verificando requisitos... ==="

# 1. Verificar se o Python está instalado
if ! command -v $PYTHON_EXEC &> /dev/null
then
    echo "ERRO: $PYTHON_EXEC não encontrado."
    echo "Por favor, instale o Python 3.12 ou superior e tente novamente."
    exit 1
fi
echo "-> Python encontrado."

# 2. Verificar se o venv já existe
if [ ! -d "$VENV_DIR" ]; then
    echo "-> Criando ambiente virtual em '$VENV_DIR'..."
    $PYTHON_EXEC -m venv $VENV_DIR
else
    echo "-> Ambiente virtual '$VENV_DIR' já existe."
fi

# 3. Ativar o ambiente virtual
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
echo "-> Ambiente virtual ativado."

# 4. Instalar dependências
echo "-> Instalando dependências de 'requirements.txt'..."
pip install -r requirements.txt > /dev/null
echo "-> Dependências instaladas."

# 5. Configurar o arquivo .env
if [ ! -f ".env" ]; then
    echo "-> Arquivo '.env' não encontrado. Criando a partir de '.env.example'..."
    cp .env.example .env
    echo "************************************************************************"
    echo "IMPORTANTE: O arquivo '.env' foi criado."
    echo "Edite-o agora para configurar sua conexão com o banco de dados PostgreSQL:"
    echo ""
    echo "Exemplo de DATABASE_URL para um banco local:"
    echo "DATABASE_URL=postgresql://SEU_USUARIO:SUA_SENHA@localhost:5432/SEU_BANCO"
    echo ""
    read -p "Pressione [Enter] quando o arquivo .env estiver configurado..."
else
    echo "-> Arquivo '.env' já existe."
fi

echo "=== Inicializando o Banco de Dados ==="
echo "-> Executando 'flask init-db' para criar as tabelas e dados iniciais..."
# A flag FLASK_APP é necessária se não estiver exportada no ambiente
export FLASK_APP=run.py
flask init-db

echo ""
echo "=========================================================="
echo "✅ Ambiente configurado com sucesso!"
echo ""
echo "Para iniciar a aplicação, execute:"
echo "   source $VENV_DIR/bin/activate"
echo "   flask run"
echo "=========================================================="

exit 0

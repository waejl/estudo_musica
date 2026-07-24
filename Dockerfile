FROM python:3.12-slim

# Evita que o Python grave arquivos .pyc no disco
ENV PYTHONDONTWRITEBYTECODE=1
# Impede que o Python envie a saída padrão para o buffer de forma assíncrona
ENV PYTHONUNBUFFERED=1

WORKDIR /workspace

# Instalar dependências do sistema necessárias para PostgreSQL e compilação
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar os requisitos do Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante da aplicação
COPY . .

# Expor a porta que o Flask/Gunicorn irá rodar
EXPOSE 5000

# Script de entrada para aguardar o Postgres e iniciar a aplicação
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "run:app"]

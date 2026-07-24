from flask import Blueprint

# Cria o Blueprint para o módulo de estudo de guitarra.
# Definimos o diretório de templates e estáticos de forma isolada.
guitar_study = Blueprint(
    "guitar_study",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static"
)

# Importações no final do arquivo para evitar importações circulares.
# As rotas e APIs do blueprint serão registradas aqui.
from app.guitar_study import routes
from app.guitar_study import auth_routes
from app.guitar_study import api_routes

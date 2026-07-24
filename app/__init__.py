import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, redirect, jsonify, request, url_for
from app.config import config_by_name
from app.extensions import db, login_manager

def create_app(config_name=None):
    """Application Factory para criar e configurar a app Flask."""
    if not config_name:
        config_name = os.environ.get("FLASK_ENV", "development")
        
    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name["default"]))
    
    # Inicializar extensões
    db.init_app(app)
    login_manager.init_app(app)
    
    # Configurar logs
    configure_logging(app)
    
    # Importar e registrar o Blueprint
    from app.guitar_study import guitar_study as guitar_study_blueprint
    app.register_blueprint(guitar_study_blueprint, url_prefix="/guitar-study")
    
    # Redirecionar a raiz da aplicação para o prefixo do Blueprint de guitarra
    @app.route("/")
    def index_redirect():
        return redirect(url_for("guitar_study.login"))
        
    # Tratamento global de erros
    register_error_handlers(app)
    
    app.logger.info("Aplicação Guitar Study inicializada com sucesso!")
    return app

def configure_logging(app):
    """Configura o sistema de logs rotativos para a aplicação."""
    if not os.path.exists("logs"):
        os.mkdir("logs")
        
    file_handler = RotatingFileHandler(
        "logs/guitar_study.log", 
        maxBytes=1024 * 1024 * 10,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s em %(module)s: %(message)s"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    
    # Desativar propagação excessiva para evitar logs em duplicidade
    app.logger.propagate = False

def register_error_handlers(app):
    """Registra tratadores de erro customizados para JSON e HTML."""
    
    @app.errorhandler(404)
    def page_not_found(e):
        # Se for uma chamada de API, retorna JSON. Caso contrário, HTML.
        if request.path.startswith("/guitar-study/api/"):
            return jsonify({
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "O recurso solicitado não foi encontrado."
                }
            }), 404
        # Aqui podemos renderizar uma página 404 específica do blueprint futuramente
        return "Página Não Encontrada (404) - Guitar Study", 404

    @app.errorhandler(500)
    def internal_server_error(e):
        app.logger.error(f"Erro interno do servidor: {str(e)}", exc_info=True)
        if request.path.startswith("/guitar-study/api/"):
            return jsonify({
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "Ocorreu um erro interno no servidor."
                }
            }), 500
        return "Erro Interno do Servidor (500) - Guitar Study", 500

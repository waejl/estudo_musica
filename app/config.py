import os
from datetime import timedelta

class Config:
    """Configuração base comum a todos os ambientes."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev_secret_key_change_in_production_12345")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Sessão persistente
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    
    # Segurança adicional
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # Definir como True em produção com HTTPS
    SESSION_COOKIE_SAMESITE = "Lax"

class DevelopmentConfig(Config):
    """Configurações para ambiente de desenvolvimento."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", 
        "postgresql://guitar_user:guitar_pass@localhost:5432/guitar_db"
    )

class TestingConfig(Config):
    """Configurações para ambiente de testes."""
    TESTING = True
    DEBUG = False
    # Evita CSRF nos testes para facilitar requisições
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL_TEST",
        "sqlite:///:memory:"  # Usado apenas para testes de unidade rápidos isolados
    )

class ProductionConfig(Config):
    """Configurações para ambiente de produção."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    # Ativa cookies seguros em produção
    SESSION_COOKIE_SECURE = True

config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}

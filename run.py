import os
import click
from dotenv import load_dotenv
from app import create_app, db
from app.guitar_study.models import User, UserSettings

# Carregar variáveis de ambiente do arquivo .env se existir
load_dotenv()

config_name = os.environ.get("FLASK_ENV", "development")
app = create_app(config_name)

@app.cli.command("init-db")
def init_db_command():
    """Limpa os dados existentes e cria novas tabelas com dados iniciais."""
    db.drop_all() # Limpa tudo para garantir um estado inicial limpo
    db.create_all()
    
    # Cria o usuário de demonstração
    demo = User(
        name="Usuário de Demonstração",
        username="demo",
        email="demo@guitarstudy.com",
        is_active=True
    )
    demo.set_password("admin123")
    db.session.add(demo)
    db.session.flush() # Gera o ID
    
    # Garante preferências do usuário de demonstração
    settings = UserSettings(
        user_id=demo.id,
        tuning_id="standard",
        fret_count=22,
        accidentals_preference="sharps",
        theme="dark"
    )
    db.session.add(settings)
    
    db.session.commit()
    click.echo("Banco de dados inicializado e semeado com o usuário 'demo'.")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

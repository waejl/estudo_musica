import os
import click
from dotenv import load_dotenv
from app import create_app, db
from app.guitar_study.models import User, UserSettings, Lesson, LessonResource, UserRole, School

# Carregar variáveis de ambiente do arquivo .env se existir
load_dotenv()

config_name = os.environ.get("FLASK_ENV", "development")
app = create_app(config_name)

def _create_user_if_not_exists(name, username, email, password, role, school=None):
    """Função helper para criar um usuário se ele não existir."""
    if User.query.filter_by(username=username).first():
        click.echo(f"Usuário '{username}' já existe. Ignorando.")
        return
    
    new_user = User(
        name=name,
        username=username,
        email=email,
        role=role,
        school=school,
        is_active=True
    )
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.flush()

    settings = UserSettings(user_id=new_user.id)
    db.session.add(settings)
    
    school_name = f"da '{school.name}'" if school else "do sistema"
    click.echo(f"-> Usuário '{username}' ({role.name.lower()}) {school_name} criado. Senha: '{password}'")

@app.cli.command("seed-defaults")
def seed_defaults_command():
    """Cria uma escola padrão e usuários de exemplo se não existirem."""
    # Cria a Escola Padrão
    default_school = School.query.filter_by(name="Escola Padrão").first()
    if not default_school:
        default_school = School(name="Escola Padrão")
        db.session.add(default_school)
        click.echo("-> Escola 'Escola Padrão' criada.")
    
    # Cria os usuários
    _create_user_if_not_exists("Super Admin", "superadmin", "super@admin.com", "super123", UserRole.SUPER_ADMIN, school=None)
    _create_user_if_not_exists("Admin da Escola", "schooladmin", "school@admin.com", "school123", UserRole.SCHOOL_ADMIN, school=default_school)
    _create_user_if_not_exists("Professor Exemplo", "teacher", "teacher@school.com", "teacher123", UserRole.TEACHER, school=default_school)
    _create_user_if_not_exists("Aluno Exemplo", "student", "student@school.com", "student123", UserRole.STUDENT, school=default_school)
    
    db.session.commit()
    click.echo("Roteiro de criação de padrões concluído.")

@app.cli.command("init-db")
def init_db_command():
    """Limpa os dados existentes e cria novas tabelas com dados iniciais."""
    click.confirm("Isso irá apagar TODOS os dados do banco. Deseja continuar?", abort=True)
    db.drop_all()
    db.create_all()
    click.echo("Tabelas do banco de dados criadas.")
    seed_defaults_command.callback()

@app.cli.command("auto-setup")
def auto_setup_command():
    """Garante que as tabelas e os dados padrão existam. Seguro para ser executado em produção."""
    db.create_all()
    click.echo("Verificando/Criando tabelas...")
    seed_defaults_command.callback()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

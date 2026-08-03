# scripts/reset_password.py
import sys
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Adicionar o diretório raiz ao sys.path para importações do Flask funcionarem
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.guitar_study.models import User, UserSettings, UserRole, School

def main():
    # Inicializa o Flask App Context
    config_name = os.environ.get("FLASK_ENV", "development")
    app = create_app(config_name)
    
    with app.app_context():
        print("=== REDEFINIÇÃO / CRIAÇÃO DE USUÁRIOS ===")
        
        # Nome do usuário
        if len(sys.argv) > 1:
            username = sys.argv[1].strip()
            print(f"Usuário informado por argumento: {username}")
        else:
            username = input("Digite o nome de usuário (username) [ex: demo]: ").strip()
            
        if not username:
            print("Erro: O nome de usuário não pode ser vazio.")
            sys.exit(1)
            
        # Senha do usuário
        if len(sys.argv) > 2:
            new_password = sys.argv[2].strip()
            print("Senha informada por argumento.")
        else:
            new_password = input("Digite a nova senha desejada: ").strip()
            
        if not new_password:
            print("Erro: A senha não pode ser vazia.")
            sys.exit(1)
            
        # Busca se o usuário existe
        user = User.query.filter_by(username=username).first()
        if user:
            print(f"-> Usuário '{username}' encontrado. Alterando a senha...")
            user.set_password(new_password)
            db.session.commit()
            print(f"Sucesso: Senha do usuário '{username}' atualizada com sucesso no banco de dados!")
        else:
            print(f"-> Usuário '{username}' não existe no banco de dados.")
            create_opt = input(f"Deseja criar um novo usuário '{username}' com a senha informada? (s/n): ").strip().lower()
            if create_opt in ['s', 'sim', 'y', 'yes']:
                name = input("Digite o nome completo do usuário [Pressione Enter para usar o padrão]: ").strip()
                if not name:
                    name = username.capitalize()
                    
                email = input("Digite o e-mail do usuário [Pressione Enter para usar o padrão]: ").strip()
                if not email:
                    email = f"{username}@estudomusica.com"
                
                # Associa à primeira escola padrão se houver
                default_school = School.query.first()
                
                # Cria o novo usuário
                new_user = User(
                    name=name,
                    username=username,
                    email=email,
                    role=UserRole.STUDENT,
                    school=default_school,
                    is_active=True
                )
                new_user.set_password(new_password)
                db.session.add(new_user)
                db.session.flush()

                # Cria as configurações padrão de usuário (UserSettings)
                settings = UserSettings(user_id=new_user.id)
                db.session.add(settings)
                
                db.session.commit()
                print(f"Sucesso: Novo usuário '{username}' (STUDENT) criado com a senha informada!")
            else:
                print("Operação cancelada pelo usuário.")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Script para criar usuários no Guitar Study
Uso: python create_user.py <username> "<nome>" <email> <senha>
  ou: python create_user.py (modo interativo)
"""
import sys
import os
import re

sys.path.insert(0, '/app')

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def create_user_interactive():
    """Modo interativo"""
    from app import create_app
    from app.extensions import db
    from app.guitar_study.models import User
    from getpass import getpass
    
    app = create_app()
    with app.app_context():
        print("\n" + "="*60)
        print("🎸 GUITAR STUDY - Criar Novo Usuário")
        print("="*60)
        
        # Verificar demo
        print("\n1️⃣  Verificando usuário 'demo'...")
        demo = User.query.filter_by(username='demo').first()
        if demo:
            print(f"   ✓ Usuário 'demo' encontrado!")
            print(f"   Email: {demo.email}")
        
        # Coletar dados
        print("\n2️⃣  Dados do novo usuário:\n")
        
        while True:
            username = input("  Username: ").strip().lower()
            if not username or len(username) < 3:
                print("  ✗ Mínimo 3 caracteres")
                continue
            if User.query.filter_by(username=username).first():
                print("  ✗ Username já existe")
                continue
            break
        
        while True:
            name = input("  Nome completo: ").strip()
            if name:
                break
        
        while True:
            email = input("  Email: ").strip()
            if validate_email(email) and not User.query.filter_by(email=email).first():
                break
            print("  ✗ Email inválido ou já registrado")
        
        while True:
            password = getpass("  Senha: ")
            if len(password) >= 6:
                if getpass("  Confirmar: ") == password:
                    break
            print("  ✗ Senhas não conferem ou muito curta (<6 chars)")
        
        # Criar
        print("\n3️⃣  Salvando...")
        try:
            user = User(username=username, name=name, email=email, is_active=True)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            print(f"\n✅ Usuário '{username}' criado com sucesso!\n")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Erro: {e}\n")
            sys.exit(1)

def create_user_cli(username, name, email, password):
    """Modo CLI com argumentos"""
    from app import create_app
    from app.extensions import db
    from app.guitar_study.models import User
    
    app = create_app()
    with app.app_context():
        # Validações
        if not username or len(username) < 3:
            print(f"❌ Username inválido (mínimo 3 chars)")
            sys.exit(1)
        
        if User.query.filter_by(username=username).first():
            print(f"❌ Username '{username}' já existe")
            sys.exit(1)
        
        if not validate_email(email):
            print(f"❌ Email '{email}' inválido")
            sys.exit(1)
        
        if User.query.filter_by(email=email).first():
            print(f"❌ Email '{email}' já registrado")
            sys.exit(1)
        
        if len(password) < 6:
            print(f"❌ Senha muito curta (mínimo 6 chars)")
            sys.exit(1)
        
        # Criar
        try:
            user = User(username=username, name=name, email=email, is_active=True)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            print(f"✅ Usuário criado: {username}")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erro: {e}")
            sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if len(sys.argv) != 5:
            print("Uso: python create_user.py <username> '<nome completo>' <email> <senha>")
            sys.exit(1)
        create_user_cli(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        create_user_interactive()

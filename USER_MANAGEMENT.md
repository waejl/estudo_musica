# 🎸 Guitar Study - Gerenciamento de Usuários

## Criar Novo Usuário

### Modo 1: CLI (Linha de Comando)
```bash
guitar-create-user <username> '<nome completo>' <email> <senha>
```

**Exemplos:**
```bash
guitar-create-user joao 'João Silva' joao@example.com senha123
guitar-create-user maria 'Maria Santos' maria@example.com prof@2024
```

### Modo 2: Interativo (com prompts)
```bash
guitar-create-user
```

Será solicitado:
1. Username (mínimo 3 caracteres)
2. Nome completo
3. Email (deve ser válido e único)
4. Senha (mínimo 6 caracteres, com confirmação)

### Modo 3: Docker direto
```bash
# CLI
docker exec guitar_study_web python /workspace/create_user.py <username> '<nome>' <email> <senha>

# Interativo
docker exec -it guitar_study_web python /workspace/create_user.py
```

## Validações

O script valida:
- ✅ Username: mínimo 3 caracteres, único
- ✅ Email: formato válido, único
- ✅ Senha: mínimo 6 caracteres
- ✅ Não permite duplicatas no banco de dados

## Usuários Padrão

| Username | Nome | Email | Papel |
|----------|------|-------|-------|
| demo | Usuário de Demonstração | demo@guitarstudy.com | Demo |
| admin | Administrador | admin@guitarstudy.com | Admin |
| professor | Professor de Guitarra | professor@guitarstudy.com | Instrutor |

## Acessar a Aplicação

- **URL**: http://200.234.212.239:5000
- **Rota de login**: http://200.234.212.239:5000/guitar-study/login

## Verificar Usuários no Banco

```bash
docker exec guitar_study_db psql -U guitar_user -d guitar_db -c "SELECT id, username, name, email FROM users ORDER BY id;"
```

## Resetar Senha de Um Usuário

```bash
docker exec -it guitar_study_web python -c "
from app import create_app
from app.extensions import db
from app.guitar_study.models import User

app = create_app()
with app.app_context():
    user = User.query.filter_by(username='admin').first()
    if user:
        user.set_password('novaSenha123')
        db.session.commit()
        print(f'Senha de {user.username} resetada')
"
```

## Troubleshooting

**Erro: "duplicate key value violates unique constraint"**
- Um usuário com esse username/email já existe
- Use outro username ou email

**Erro: "psycopg2.errors.OperationalError"**
- Banco de dados não está rodando
- Verifique: `docker ps | grep guitar_study_db`

**Modo interativo não funciona**
- Use modo CLI em vez de interativo
- Modo interativo requer terminal TTY

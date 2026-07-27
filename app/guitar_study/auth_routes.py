from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.guitar_study import guitar_study
from app.guitar_study.models import User, UserSettings

@guitar_study.route("/login", methods=["GET", "POST"])
def login():
    """Rota para autenticação do usuário."""
    if current_user.is_authenticated:
        return redirect(url_for("guitar_study.dashboard"))
        
    if request.method == "POST":
        username_or_email = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        remember = True if request.form.get("remember") else False
        
        if not username_or_email or not password:
            flash("Por favor, preencha todos os campos.", "danger")
            return render_template("guitar_study/login.html")
            
        # Tenta buscar por username ou por email
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash("Esta conta está desativada.", "danger")
                return render_template("guitar_study/login.html")
                
            # Atualiza o último login
            user.last_login_at = datetime.utcnow()
            db.session.commit()
            
            login_user(user, remember=remember)
            session.permanent = True
            
            # Log de sucesso
            from flask import current_app
            current_app.logger.info(f"Usuário {user.username} realizou login com sucesso.")
            
            next_page = request.args.get("next")
            return redirect(next_page) if next_page and next_page.startswith("/guitar-study") else redirect(url_for("guitar_study.dashboard"))
            
        flash("Credenciais inválidas. Verifique seu usuário/e-mail e senha.", "danger")
        
        # Log de falha
        from flask import current_app
        current_app.logger.warning(f"Falha de login para o identificador: {username_or_email}")
        
    return render_template("guitar_study/login.html")


@guitar_study.route("/register", methods=["GET", "POST"])
def register():
    """Rota para registro de um novo usuário."""
    if current_user.is_authenticated:
        return redirect(url_for("guitar_study.dashboard"))
        
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        username = request.form.get("username", "").strip().lower()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        
        if not name or not username or not email or not password or not confirm_password:
            flash("Todos os campos são obrigatórios.", "danger")
            return render_template("guitar_study/register.html")
            
        if password != confirm_password:
            flash("As senhas informadas não coincidem.", "danger")
            return render_template("guitar_study/register.html")
            
        if len(password) < 6:
            flash("A senha deve conter pelo menos 6 caracteres.", "danger")
            return render_template("guitar_study/register.html")
            
        # Verifica se username ou e-mail já existem
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            if existing_user.username == username:
                flash("Este nome de usuário já está cadastrado.", "danger")
            else:
                flash("Este e-mail já está cadastrado.", "danger")
            return render_template("guitar_study/register.html")
            
        try:
            # Cria o usuário
            new_user = User(name=name, username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.flush()  # Para obter o id gerado
            
            # Cria as configurações padrão de preferência
            default_settings = UserSettings(
                user_id=new_user.id,
                tuning_id="standard",
                fret_count=22,
                accidentals_preference="sharps",
                theme="dark"
            )
            db.session.add(default_settings)
            db.session.commit()
            
            # Log de criação de usuário
            from flask import current_app
            current_app.logger.info(f"Novo usuário criado: {username} (ID: {new_user.id})")
            
            flash("Cadastro realizado com sucesso! Faça seu login.", "success")
            return redirect(url_for("guitar_study.login"))
            
        except Exception as e:
            db.session.rollback()
            from flask import current_app
            current_app.logger.error(f"Erro ao cadastrar usuário {username}: {str(e)}", exc_info=True)
            flash("Ocorreu um erro no processamento do seu cadastro. Tente novamente.", "danger")
            
    return render_template("guitar_study/register.html")


@guitar_study.route("/logout")
@login_required
def logout():
    """Rota para encerramento da sessão."""
    username = current_user.username
    logout_user()
    
    from flask import current_app
    current_app.logger.info(f"Usuário {username} deslogado do sistema.")
    
    flash("Sessão encerrada com sucesso.", "info")
    return redirect(url_for("guitar_study.login"))


@guitar_study.route("/settings/profile", methods=["POST"])
@login_required
def update_profile():
    """Atualiza as informações de perfil do usuário (nome, e-mail, senha)."""
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "")
    
    if not name or not email:
        flash("Nome e e-mail são obrigatórios.", "danger")
        return redirect(url_for("guitar_study.settings"))
        
    # Verifica se e-mail já existe em outro usuário
    existing_email = User.query.filter(User.email == email, User.id != current_user.id).first()
    if existing_email:
        flash("Este endereço de e-mail já está em uso por outro usuário.", "danger")
        return redirect(url_for("guitar_study.settings"))
        
    try:
        current_user.name = name
        current_user.email = email
        
        # Se desejar alterar a senha, valida a senha atual
        if new_password:
            if not current_password:
                flash("Você deve informar a senha atual para cadastrar uma nova senha.", "danger")
                return redirect(url_for("guitar_study.settings"))
                
            if not current_user.check_password(current_password):
                flash("Senha atual incorreta.", "danger")
                return redirect(url_for("guitar_study.settings"))
                
            if len(new_password) < 6:
                flash("A nova senha deve ter no mínimo 6 caracteres.", "danger")
                return redirect(url_for("guitar_study.settings"))
                
            current_user.set_password(new_password)
            
        db.session.commit()
        flash("Perfil atualizado com sucesso!", "success")
    except Exception as e:
        db.session.rollback()
        flash("Erro ao atualizar o perfil. Tente novamente.", "danger")
        
    return redirect(url_for("guitar_study.settings"))


@guitar_study.route("/settings/preferences", methods=["POST"])
@login_required
def update_preferences():
    """Atualiza as preferências musicais e visuais do usuário."""
    tuning_id = request.form.get("tuning_id", "standard")
    fret_count = int(request.form.get("fret_count", 22))
    accidentals_preference = request.form.get("accidentals_preference", "sharps")
    theme = request.form.get("theme", "dark")
    
    # Validações básicas
    if fret_count not in [21, 22, 24]:
        fret_count = 22
    if accidentals_preference not in ["sharps", "flats"]:
        accidentals_preference = "sharps"
    if theme not in ["dark", "light"]:
        theme = "dark"
        
    try:
        settings = current_user.settings
        if not settings:
            settings = UserSettings(user_id=current_user.id)
            db.session.add(settings)
            
        settings.tuning_id = tuning_id
        settings.fret_count = fret_count
        settings.accidentals_preference = accidentals_preference
        settings.theme = theme
        
        db.session.commit()
        flash("Preferências atualizadas com sucesso!", "success")
    except Exception as e:
        db.session.rollback()
        flash("Erro ao salvar suas preferências musicais.", "danger")
        
    return redirect(url_for("guitar_study.settings"))


@guitar_study.route("/settings/preferences/custom", methods=["POST"])
@login_required
def create_custom_tuning():
    """Cria uma afinação personalizada para o usuário."""
    name = request.form.get("name", "").strip()
    notes = request.form.get("notes", "").strip().upper()
    
    if not name or not notes:
        return jsonify({"success": False, "error": "Nome e Notas são obrigatórios"}), 400
        
    # Validação simples
    split_notes = notes.split()
    if len(split_notes) != 6:
        return jsonify({"success": False, "error": "Devem ser fornecidas exatamente 6 notas"}), 400
        
    try:
        from app.guitar_study.models import CustomTuning
        custom = CustomTuning(
            user_id=current_user.id,
            name=name,
            notes=notes
        )
        db.session.add(custom)
        db.session.commit()
        return jsonify({"success": True, "data": {"id": custom.id, "name": custom.name}})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": f"Erro interno do servidor: {str(e)}"}), 500


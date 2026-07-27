# app/super_admin/routes.py
from functools import wraps
from flask import render_template, abort, redirect, url_for, flash, session
from flask_login import login_required, current_user, login_user
from app.extensions import db
from app.guitar_study.models import User, School, UserRole
from . import super_admin_bp

def super_admin_required(f):
    """Garante acesso exclusivo ao Superadmin do sistema."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Permite acesso se for superadmin OU se houver um ID de superadmin na sessão (para poder parar o impersonate)
        is_impersonating = session.get('superadmin_user_id') is not None
        if not current_user.is_authenticated or (not current_user.is_super_admin and not is_impersonating):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@super_admin_bp.route("/dashboard")
@login_required
@super_admin_required
def dashboard():
    """Painel geral do Superadmin com a listagem de escolas e seus usuários."""
    schools = School.query.order_by(School.name.asc()).all()
    # Pega também o superadmin original para fins de exibição se estiver impersonando
    superadmin_orig = None
    if session.get('superadmin_user_id'):
        superadmin_orig = User.query.get(session.get('superadmin_user_id'))
        
    return render_template("super_admin/dashboard.html", schools=schools, superadmin_orig=superadmin_orig)

@super_admin_bp.route("/impersonate/<int:user_id>", methods=["POST"])
@login_required
@super_admin_required
def impersonate(user_id):
    """Assume a identidade de um usuário específico."""
    target_user = db.get_or_404(User, user_id)
    
    if target_user.is_super_admin:
        flash("Você não pode assumir outro Superadmin.", "danger")
        return redirect(url_for('super_admin.dashboard'))
        
    # Salva o ID do superadmin real na sessão se ainda não estiver salvo (evita loops)
    if 'superadmin_user_id' not in session:
        session['superadmin_user_id'] = current_user.id
        
    # Efetua o login do usuário alvo
    login_user(target_user)
    flash(f"Você agora está logado como '{target_user.name}' ({target_user.role.name.lower()}).", "success")
    
    # Redireciona para o destino apropriado com base no novo perfil
    if target_user.is_school_admin or target_user.is_teacher:
        return redirect(url_for('school_admin.dashboard'))
    return redirect(url_for('guitar_study.dashboard'))

@super_admin_bp.route("/stop-impersonate", methods=["POST", "GET"])
@login_required
def stop_impersonate():
    """Para a impersonation e retorna ao perfil do Superadmin."""
    superadmin_id = session.pop('superadmin_user_id', None)
    if not superadmin_id:
        flash("Você não está em modo de impersonation.", "warning")
        return redirect(url_for('guitar_study.dashboard'))
        
    super_user = db.get_or_404(User, superadmin_id)
    login_user(super_user)
    flash("Retornado ao perfil de Superadmin com sucesso.", "success")
    return redirect(url_for('super_admin.dashboard'))

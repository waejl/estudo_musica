# app/school_admin/routes.py
import os
import base64
import uuid
import time
from functools import wraps
from werkzeug.utils import secure_filename
from flask import render_template, abort, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from sqlalchemy import func, or_
from app.extensions import db
from app.guitar_study.models import User, Lesson, LessonResource, UserRole, StepMedia, LessonProgress, StudySession
from . import school_admin_bp
from .forms import LessonForm, ResourceForm, UserAdminForm, UserCreateForm

# --- Helper functions ---

def process_media_input(data, lesson_id, school_id, resource_type):
    """
    Detecta se o dado é base64 ou data-URI. Se sim, salva como arquivo e retorna o caminho.
    Se não, retorna o dado original como caminho.
    """
    if not data or not isinstance(data, str):
        return data

    # Se começar com data:, extrai o base64
    base64_str = data
    if data.startswith('data:'):
        # Ex: "data:image/svg+xml;base64,..."
        if ',' in data:
            base64_str = data.split(',')[1]
        else:
            return data # Formato inválido, retorna original

    # Se for base64 longo (heurística), processa
    if len(base64_str) > 100 and not base64_str.startswith('uploads/'):
        # Gerar nome e extensão
        ext = 'jpg'
        if resource_type == 'pdf': ext = 'pdf'
        elif resource_type == 'image': ext = 'jpeg'
        
        school_prefix = "base" if school_id is None else str(school_id)
        filename = f"{school_prefix}_{lesson_id}_{int(time.time())}_{uuid.uuid4().hex[:8]}.{ext}"
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        try:
            with open(upload_path, "wb") as fh:
                fh.write(base64.b64decode(base64_str))
            return os.path.join('uploads', filename).replace('\\', '/')
        except Exception as e:
            current_app.logger.error(f"Erro ao salvar base64: {e}")
            return None
            
    return data


def normalize_lesson_text(value):
    """Aceita lista ou texto no JSON e armazena em linhas simples."""
    if isinstance(value, list):
        return "\n".join(str(item).strip() for item in value if str(item).strip())
    if value is None:
        return None
    return str(value).strip() or None


def normalize_json_text(value):
    """Armazena dict/list como JSON; strings passam sem alteracao."""
    import json
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    if value is None:
        return None
    return str(value).strip() or None


def split_lesson_text(value):
    """Exporta campos multiline como lista para facilitar manutencao do JSON."""
    if not value:
        return []
    return [line.strip() for line in value.splitlines() if line.strip()]


def normalize_export_json(value):
    """Exporta JSON armazenado como objeto quando possivel."""
    import json
    if not value:
        return {}
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return value

# --- Decorators de Permissão ---

def school_admin_required(f):
    """Garante acesso exclusivo ao Administrador da Escola local."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_school_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def teacher_or_school_admin_required(f):
    """Garante acesso a Professores, Admins de Escola e Super Admin."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not (
            current_user.is_teacher or current_user.is_school_admin or current_user.is_super_admin
        ):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# --- Rotas do Painel da Escola ---

@school_admin_bp.route("/dashboard")
@login_required
@teacher_or_school_admin_required
def dashboard():
    """Página inicial do painel da escola."""
    if current_user.is_super_admin:
        users_query = User.query
        lessons_query = Lesson.query.filter_by(school_id=None)
    else:
        users_query = User.query.filter_by(school_id=current_user.school_id)
        lessons_query = Lesson.query.filter(
            or_(Lesson.school_id == current_user.school_id, Lesson.school_id == None)
        )

    student_ids = [u.id for u in users_query.filter_by(role=UserRole.STUDENT).all()]
    progress_query = LessonProgress.query.filter(LessonProgress.user_id.in_(student_ids)) if student_ids else LessonProgress.query.filter(False)
    recent_progress = progress_query.order_by(LessonProgress.updated_at.desc()).limit(8).all()
    total_minutes = db.session.query(func.sum(StudySession.duration_minutes)).filter(StudySession.user_id.in_(student_ids)).scalar() if student_ids else 0

    stats = {
        "students_count": len(student_ids),
        "published_lessons_count": lessons_query.filter_by(is_published=True).count(),
        "in_progress_count": progress_query.filter_by(status="in_progress").count(),
        "completed_count": progress_query.filter_by(status="completed").count(),
        "total_minutes": total_minutes or 0,
    }
    return render_template("school_admin/dashboard.html", stats=stats, recent_progress=recent_progress)

# --- CRUD de Aulas ---

@school_admin_bp.route("/lessons")
@login_required
@teacher_or_school_admin_required
def manage_lessons():
    """Página para gerenciar as aulas da escola ou as aulas base (se for Superadmin)."""
    if current_user.is_super_admin:
        # O superadmin gerencia exclusivamente as Aulas Base (school_id == None)
        lessons = Lesson.query.filter_by(school_id=None).order_by(Lesson.order.asc()).all()
    else:
        # Mostra as aulas da escola do usuário E as aulas base (sem escola)
        lessons = Lesson.query.filter(
            or_(Lesson.school_id == current_user.school_id, Lesson.school_id == None)
        ).order_by(Lesson.school_id.isnot(None), Lesson.order.asc()).all()
    return render_template("school_admin/lessons.html", lessons=lessons)

@school_admin_bp.route("/lessons/new", methods=["GET", "POST"])
@login_required
@teacher_or_school_admin_required
def new_lesson():
    """Rota para criar uma nova aula."""
    form = LessonForm()
    if form.validate_on_submit():
        # Se for superadmin, cria uma Aula Base (school_id = None)
        school_id = None if current_user.is_super_admin else current_user.school_id
        new_lesson = Lesson(
            title=form.title.data,
            description=form.description.data,
            module=form.module.data,
            level=form.level.data or None,
            estimated_minutes=form.estimated_minutes.data,
            objectives=form.objectives.data,
            prerequisites=form.prerequisites.data,
            practice_focus=form.practice_focus.data,
            order=form.order.data,
            is_published=form.is_published.data,
            school_id=school_id
        )
        db.session.add(new_lesson)
        db.session.commit()
        flash("Aula criada com sucesso! Agora adicione recursos a ela.", "success")
        return redirect(url_for("school_admin.edit_lesson", lesson_id=new_lesson.id))
    return render_template("school_admin/lesson_form.html", form=form)

@school_admin_bp.route("/lessons/<int:lesson_id>/edit", methods=["GET", "POST"])
@login_required
@teacher_or_school_admin_required
def edit_lesson(lesson_id):
    """Rota para editar uma aula."""
    lesson = db.get_or_404(Lesson, lesson_id)
    
    # Validação de permissões
    if current_user.is_super_admin:
        if lesson.school_id is not None:
            flash("Como Superadmin, você gerencia as aulas das escolas diretamente assumindo o perfil da empresa.", "warning")
            return redirect(url_for('school_admin.manage_lessons'))
    else:
        if lesson.school_id != current_user.school_id:
            flash("Você não tem permissão para editar esta aula.", "danger")
            return redirect(url_for('school_admin.manage_lessons'))

    form = LessonForm(obj=lesson)
    resource_form = ResourceForm()
    if form.validate_on_submit() and 'title' in request.form:
        lesson.title = form.title.data
        lesson.description = form.description.data
        lesson.module = form.module.data
        lesson.level = form.level.data or None
        lesson.estimated_minutes = form.estimated_minutes.data
        lesson.objectives = form.objectives.data
        lesson.prerequisites = form.prerequisites.data
        lesson.practice_focus = form.practice_focus.data
        lesson.order = form.order.data
        lesson.is_published = form.is_published.data
        db.session.commit()
        flash("Aula atualizada com sucesso!", "success")
        return redirect(url_for("school_admin.edit_lesson", lesson_id=lesson.id))

    return render_template("school_admin/lesson_form.html", form=form, resource_form=resource_form, lesson=lesson)

@school_admin_bp.route("/lessons/<int:lesson_id>/delete", methods=["POST"])
@login_required
@teacher_or_school_admin_required
def delete_lesson(lesson_id):
    """Rota para excluir uma aula."""
    lesson = db.get_or_404(Lesson, lesson_id)
    
    # Validação de permissões
    if current_user.is_super_admin:
        if lesson.school_id is not None:
            flash("Operação não permitida.", "danger")
            return redirect(url_for('school_admin.manage_lessons'))
    else:
        if lesson.school_id != current_user.school_id:
            flash("Você não tem permissão para excluir esta aula.", "danger")
            return redirect(url_for('school_admin.manage_lessons'))

    for resource in lesson.resources:
        if resource.resource_type in ['pdf', 'image']:
            try:
                private_base = os.path.dirname(current_app.config['UPLOAD_FOLDER'])
                file_path = os.path.join(private_base, resource.path)
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception: pass
    
    db.session.delete(lesson)
    db.session.commit()
    flash("Aula excluída com sucesso.", "success")
    return redirect(url_for("school_admin.manage_lessons"))

# --- Gerenciamento de Recursos ---

@school_admin_bp.route("/lessons/<int:lesson_id>/add_resource", methods=["POST"])
@login_required
@teacher_or_school_admin_required
def add_resource(lesson_id):
    lesson = db.get_or_404(Lesson, lesson_id)
    
    # Permissões
    if not current_user.is_super_admin and lesson.school_id != current_user.school_id:
        abort(403)
    
    form = ResourceForm()
    if form.validate_on_submit():
        path = None
        resource_type = form.resource_type.data

        # Log para depuração profunda
        current_app.logger.debug(f"DEBUG: add_resource | type: {resource_type} | request.files: {request.files.keys()} | request.form: {request.form}")

        if resource_type in ['pdf', 'image']:
            file = request.files.get('file')
            # Depuração detalhada
            current_app.logger.debug(f"DEBUG: Arquivo recebido: {file}")
            if file:
                current_app.logger.debug(f"DEBUG: Filename: {file.filename}, ContentType: {file.content_type}")
            
            if file and file.filename:
                school_prefix = "base" if current_user.is_super_admin else str(lesson.school_id)
                filename = secure_filename(f"{school_prefix}_{lesson.id}_{file.filename}")
                upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(upload_path)
                path = os.path.join('uploads', filename).replace('\\', '/')
            else:
                current_app.logger.warning(f"DEBUG: Arquivo ausente ou filename vazio para {resource_type}. Objeto file: {file}")
                flash("Para este tipo de recurso, o arquivo é obrigatório.", "danger")
                return redirect(url_for('school_admin.edit_lesson', lesson_id=lesson.id))
        elif resource_type in ['youtube_url', 'video_url']:
            path = form.url.data
            if not path:
                flash("Para este tipo de recurso, a URL é obrigatória.", "danger")
                return redirect(url_for('school_admin.edit_lesson', lesson_id=lesson.id))
        
        # Criação do recurso (path pode ser None se for 'none')
        new_resource = LessonResource(
            lesson_id=lesson.id, 
            title=form.title.data, 
            content=form.content.data, 
            resource_type=resource_type, 
            path=path,
            exercise_type=form.exercise_type.data or None,
            exercise_params=normalize_json_text(form.exercise_params.data),
            checklist_items=normalize_lesson_text(form.checklist_items.data)
        )
        db.session.add(new_resource)
        db.session.commit()
        flash("Etapa adicionada com sucesso!", "success")
    else:
        # Log de erro de validação do form
        current_app.logger.error(f"DEBUG: Form errors: {form.errors}")
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Erro no campo '{getattr(form, field).label.text}': {error}", "danger")
    return redirect(url_for('school_admin.edit_lesson', lesson_id=lesson.id))

@school_admin_bp.route("/resource/<int:resource_id>/delete", methods=["POST"])
@login_required
@teacher_or_school_admin_required
def delete_resource(resource_id):
    """Exclui uma etapa de conteúdo de uma aula."""
    resource = db.get_or_404(LessonResource, resource_id)
    lesson = resource.lesson
    
    # Permissões
    if not current_user.is_super_admin and lesson.school_id != current_user.school_id:
        abort(403)

    if resource.resource_type in ['pdf', 'image']:
        try:
            private_base = os.path.dirname(current_app.config['UPLOAD_FOLDER'])
            file_path = os.path.join(private_base, resource.path)
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            flash(f"Não foi possível remover o arquivo físico: {e}", "warning")

    db.session.delete(resource)
    db.session.commit()
    flash("Recurso removido com sucesso.", "success")
    return redirect(url_for('school_admin.edit_lesson', lesson_id=lesson.id))

@school_admin_bp.route("/resource/<int:resource_id>/edit", methods=["POST"])
@login_required
@teacher_or_school_admin_required
def edit_resource(resource_id):
    resource = db.get_or_404(LessonResource, resource_id)
    lesson = resource.lesson
    if not current_user.is_super_admin and lesson.school_id != current_user.school_id:
        abort(403)
        
    resource.title = request.form.get('title')
    resource.content = request.form.get('content')
    db.session.commit()
    flash("Etapa atualizada!", "success")
    return redirect(url_for('school_admin.edit_lesson', lesson_id=lesson.id))

@school_admin_bp.route("/resource/<int:resource_id>/move/<direction>", methods=["POST"])
@login_required
@teacher_or_school_admin_required
def move_resource(resource_id, direction):
    resource = db.get_or_404(LessonResource, resource_id)
    lesson = resource.lesson
    if not current_user.is_super_admin and lesson.school_id != current_user.school_id:
        abort(403)
    
    # Lógica simples de ordenação (swap)
    resources = list(lesson.resources.order_by(LessonResource.order.asc()).all())
    idx = resources.index(resource)
    
    if direction == 'up' and idx > 0:
        other = resources[idx-1]
        resource.order, other.order = other.order, resource.order
    elif direction == 'down' and idx < len(resources) - 1:
        other = resources[idx+1]
        resource.order, other.order = other.order, resource.order
    
    db.session.commit()
    return redirect(url_for('school_admin.edit_lesson', lesson_id=lesson.id))


# --- Rotas de Gerenciamento de Usuários (da Escola) ---

@school_admin_bp.route("/users")
@login_required
@school_admin_required
def manage_users():
    """Página para gerenciar os usuários da própria escola (apenas para Admin da Escola local)."""
    users = User.query.filter(User.school_id == current_user.school_id).order_by(User.id.asc()).all()
    return render_template("school_admin/users.html", users=users)

@school_admin_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
@school_admin_required
def edit_user(user_id):
    """Rota para um admin de escola editar um usuário da sua escola."""
    user = db.get_or_404(User, user_id)
    if user.school_id != current_user.school_id or user.is_school_admin:
        flash("Você não tem permissão para editar este usuário.", "danger")
        return redirect(url_for('school_admin.manage_users'))

    form = UserAdminForm(obj=user)
    form.role.choices = [
        (UserRole.STUDENT.value, UserRole.STUDENT.name.title()),
        (UserRole.TEACHER.value, UserRole.TEACHER.name.title())
    ]
    if form.validate_on_submit():
        user.role = UserRole(form.role.data)
        user.is_active = form.is_active.data
        db.session.commit()
        flash(f"Usuário '{user.username}' updated com sucesso!", "success")
        return redirect(url_for('school_admin.manage_users'))

    return render_template("school_admin/user_form.html", form=form, user=user)


@school_admin_bp.route("/users/new", methods=["GET", "POST"])
@login_required
@school_admin_required
def new_user():
    """Rota para o admin da escola registrar novos professores e alunos."""
    form = UserCreateForm()
    if form.validate_on_submit():
        # Verifica se o login (username) já está em uso
        if User.query.filter_by(username=form.username.data).first():
            flash("Este nome de usuário (login) já está sendo utilizado.", "danger")
            return render_template("school_admin/user_create_form.html", form=form)
            
        # Verifica se o email já está cadastrado
        if User.query.filter_by(email=form.email.data).first():
            flash("Este endereço de email já está cadastrado no sistema.", "danger")
            return render_template("school_admin/user_create_form.html", form=form)
            
        # Cria o usuário atrelado à escola do administrador atual
        new_user = User(
            name=form.name.data,
            username=form.username.data,
            email=form.email.data,
            role=UserRole(form.role.data),
            school_id=current_user.school_id,
            is_active=True
        )
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.flush() # Gera o ID do usuário para as preferências
        
        # Cria as configurações padrão de braço e tema para o novo usuário
        from app.guitar_study.models import UserSettings
        settings = UserSettings(user_id=new_user.id)
        db.session.add(settings)
        
        db.session.commit()
        flash(f"Usuário '{new_user.name}' ({new_user.role.name.lower()}) registrado com sucesso!", "success")
        return redirect(url_for('school_admin.manage_users'))
        
    return render_template("school_admin/user_create_form.html", form=form)


@school_admin_bp.route("/lessons/import", methods=["POST"])
@login_required
@teacher_or_school_admin_required
def import_lessons():
    """Rota para importar aulas e etapas em lote a partir de um arquivo JSON."""
    import json
    from app.guitar_study.models import StepMedia
    
    file = request.files.get('json_file')
    if not file or not file.filename.endswith('.json'):
        flash("Por favor, selecione um arquivo JSON válido.", "danger")
        return redirect(url_for('school_admin.manage_lessons'))
        
    try:
        # Lê e decodifica o arquivo enviado
        file_content = file.read().decode('utf-8')
        lessons_data = json.loads(file_content)
        
        # Garante que o arquivo é uma lista de aulas
        if not isinstance(lessons_data, list):
            flash("Formato do JSON incorreto. O arquivo deve conter uma lista (array) de aulas.", "danger")
            return redirect(url_for('school_admin.manage_lessons'))
            
        lessons_created = 0
        steps_created = 0
        medias_created = 0
        
        # Define o school_id com base no perfil de quem está importando
        school_id = None if current_user.is_super_admin else current_user.school_id
        
        # Processa cada aula de forma sequencial
        for l_data in lessons_data:
            title = l_data.get('title')
            description = l_data.get('description', '')
            module = l_data.get('module')
            level = l_data.get('level')
            estimated_minutes = l_data.get('estimated_minutes')
            objectives = normalize_lesson_text(l_data.get('objectives'))
            prerequisites = normalize_lesson_text(l_data.get('prerequisites'))
            practice_focus = normalize_lesson_text(l_data.get('practice_focus'))
            order = l_data.get('order', 0)
            is_published = l_data.get('is_published', True)
            
            if not title:
                continue # Pula aulas sem título obrigatório
                
            # Cria a aula
            new_lesson = Lesson(
                title=title,
                description=description,
                module=module,
                level=level,
                estimated_minutes=estimated_minutes,
                objectives=objectives,
                prerequisites=prerequisites,
                practice_focus=practice_focus,
                order=order,
                is_published=is_published,
                school_id=school_id
            )
            db.session.add(new_lesson)
            db.session.flush() # Gera o ID da aula para ligar os passos
            lessons_created += 1
            
            # Cria as etapas (steps) associadas a esta aula
            steps_list = l_data.get('steps', [])
            if isinstance(steps_list, list):
                for idx, s_data in enumerate(steps_list):
                    s_title = s_data.get('title')
                    s_content = s_data.get('content', '')
                    s_type = s_data.get('resource_type', 'none') # Default para 'none' (apenas texto)
                    s_path = s_data.get('path', None)
                    
                    if not s_title:
                        continue # Pula etapas sem dados mínimos obrigatórios
                        
                    # Trata o youtube embed se necessário
                    if s_type == 'youtube_url' and s_path:
                        try:
                            video_id = None
                            if "v=" in s_path:
                                video_id = s_path.split("v=")[1].split("&")[0]
                            elif "youtu.be/" in s_path:
                                video_id = s_path.split("youtu.be/")[1].split("?")[0]
                        except Exception: pass

                    new_step = LessonResource(
                        lesson_id=new_lesson.id,
                        title=s_title,
                        content=s_content,
                        resource_type=s_type,
                        path=process_media_input(s_path, new_lesson.id, school_id, s_type),
                        exercise_type=s_data.get('exercise_type') or None,
                        exercise_params=normalize_json_text(s_data.get('exercise_params')),
                        checklist_items=normalize_lesson_text(s_data.get('checklist_items')),
                        order=s_data.get('order', idx + 1)
                    )
                    db.session.add(new_step)
                    db.session.flush() # Gera o ID do recurso para poder salvar mídias secundárias
                    steps_created += 1
                    
                    # Processa mídias secundárias (se houver o array 'media_items')
                    media_list = s_data.get('media_items', [])
                    if isinstance(media_list, list):
                        for m_idx, m_data in enumerate(media_list):
                            m_title = m_data.get('title')
                            m_type = m_data.get('media_type')
                            m_path = m_data.get('path')
                            
                            if not m_type or not m_path:
                                continue
                                
                            new_media = StepMedia(
                                resource_id=new_step.id,
                                title=m_title,
                                media_type=m_type,
                                path=process_media_input(m_path, new_lesson.id, school_id, m_type),
                                order=m_data.get('order', m_idx + 1)
                            )
                            db.session.add(new_media)
                            medias_created += 1
                    
        db.session.commit()
        
        tipo_aula = "Aulas Base" if current_user.is_super_admin else "Aulas da Escola"
        flash(f"Importação concluída com sucesso! {lessons_created} {tipo_aula}, {steps_created} etapas e {medias_created} mídias anexadas foram registradas.", "success")
        
    except json.JSONDecodeError:
        flash("Erro ao processar o arquivo. O JSON possui erros de sintaxe ou formatação.", "danger")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro durante a importação de JSON: {str(e)}", exc_info=True)
        flash(f"Ocorreu um erro interno ao importar as aulas: {str(e)}", "danger")
        
    return redirect(url_for('school_admin.manage_lessons'))


@school_admin_bp.route("/lessons/export", methods=["GET"])
@login_required
@teacher_or_school_admin_required
def export_lessons():
    """Gera um arquivo JSON de backup contendo todas as aulas, etapas e múltiplas mídias."""
    import json
    from flask import Response
    
    # Filtra as aulas com base no perfil de quem está exportando
    if current_user.is_super_admin:
        lessons = Lesson.query.filter_by(school_id=None).order_by(Lesson.order.asc()).all()
    else:
        lessons = Lesson.query.filter_by(school_id=current_user.school_id).order_by(Lesson.order.asc()).all()
        
    lessons_list = []
    
    # Monta a estrutura JSON aninhada das aulas, etapas e suas mídias
    for lesson in lessons:
        lesson_dict = {
            "title": lesson.title,
            "description": lesson.description,
            "module": lesson.module,
            "level": lesson.level,
            "estimated_minutes": lesson.estimated_minutes,
            "objectives": split_lesson_text(lesson.objectives),
            "prerequisites": split_lesson_text(lesson.prerequisites),
            "practice_focus": lesson.practice_focus,
            "order": lesson.order,
            "is_published": lesson.is_published,
            "steps": []
        }
        
        for resource in lesson.resources.order_by(LessonResource.order.asc()):
            step_dict = {
                "title": resource.title,
                "content": resource.content,
                "resource_type": resource.resource_type,
                "path": resource.path,
                "exercise_type": resource.exercise_type,
                "exercise_params": normalize_export_json(resource.exercise_params),
                "checklist_items": split_lesson_text(resource.checklist_items),
                "order": resource.order,
                "media_items": []
            }
            
            for media in resource.media_items.order_by(StepMedia.order.asc()):
                step_dict["media_items"].append({
                    "title": media.title,
                    "media_type": media.media_type,
                    "path": media.path,
                    "order": media.order
                })
                
            lesson_dict["steps"].append(step_dict)
            
        lessons_list.append(lesson_dict)
        
    # Transforma em string JSON identada
    json_data = json.dumps(lessons_list, indent=2, ensure_ascii=False)
    
    # Nome de arquivo dinâmico e amigável
    if current_user.is_super_admin:
        filename = "backup_aulas_base.json"
    else:
        filename = f"backup_aulas_escola_{current_user.school_id}.json"
        
    # Envia como resposta de anexo para download direto
    return Response(
        json_data,
        mimetype="application/json",
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )


# --- Gerenciamento de Mídias Adicionais (Etapas Ricas) ---

@school_admin_bp.route("/resource/<int:resource_id>/add_media", methods=["POST"])
@login_required
@teacher_or_school_admin_required
def add_media(resource_id):
    """Adiciona uma mídia extra (PDF, Imagem, Vídeo ou Braço) a uma etapa específica."""
    from app.guitar_study.models import StepMedia
    
    resource = db.get_or_404(LessonResource, resource_id)
    lesson = resource.lesson
    
    # Permissão: Superadmin pode tudo em aulas base. Escola só na escola dela.
    if not current_user.is_super_admin and lesson.school_id != current_user.school_id:
        abort(403)
        
    title = request.form.get('media_title')
    media_type = request.form.get('media_type')
    path = None
    
    if media_type in ['pdf', 'image']:
        file = request.files.get('media_file')
        if file:
            school_prefix = "base" if current_user.is_super_admin else str(lesson.school_id)
            filename = secure_filename(f"{school_prefix}_extra_{resource.id}_{file.filename}")
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(upload_path)
            path = os.path.join('uploads', filename).replace('\\', '/')
        else:
            flash("O arquivo é obrigatório para este tipo de mídia.", "danger")
            
    elif media_type in ['youtube_url', 'video_url']:
        path = request.form.get('media_url')
        if not path:
            flash("A URL é obrigatória para este tipo de mídia.", "danger")
            
    elif media_type == 'fretboard':
        # Captura as marcações do braço da guitarra em formato JSON string do formulário
        path = request.form.get('fretboard_data')
        if not path:
            flash("Nenhuma nota marcada no braço foi recebida.", "danger")
            
    if path:
        # Pega o próximo número de ordem
        existing_medias = resource.media_items.count()
        new_media = StepMedia(
            resource_id=resource.id,
            title=title if title else f"Anexo {existing_medias + 1}",
            media_type=media_type,
            path=path,
            order=existing_medias + 1
        )
        db.session.add(new_media)
        db.session.commit()
        flash("Mídia adicional anexada com sucesso!", "success")
        
    return redirect(url_for('school_admin.edit_lesson', lesson_id=lesson.id))


@school_admin_bp.route("/media/<int:media_id>/delete", methods=["POST"])
@login_required
@teacher_or_school_admin_required
def delete_media(media_id):
    """Exclui uma mídia adicional atrelada a uma etapa."""
    from app.guitar_study.models import StepMedia
    
    media = db.get_or_404(StepMedia, media_id)
    resource = media.resource
    lesson = resource.lesson
    
    if not current_user.is_super_admin and lesson.school_id != current_user.school_id:
        abort(403)
        
    # Se for um arquivo físico local, remove do disco
    if media.media_type in ['pdf', 'image']:
        try:
            private_base = os.path.dirname(current_app.config['UPLOAD_FOLDER'])
            file_path = os.path.join(private_base, media.path)
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            flash(f"Aviso: Não foi possível remover o arquivo físico: {e}", "warning")
            
    db.session.delete(media)
    db.session.commit()
    flash("Mídia adicional removida com sucesso.", "success")
    return redirect(url_for('school_admin.edit_lesson', lesson_id=lesson.id))

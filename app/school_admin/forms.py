# app/admin/forms.py
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, IntegerField, BooleanField, SubmitField, SelectField, PasswordField, HiddenField
from wtforms.validators import DataRequired, Length, Optional, URL, Email

class LessonForm(FlaskForm):
    """Formulário para criar e editar aulas básicas."""
    title = StringField(
        "Título da Aula",
        validators=[DataRequired(), Length(min=3, max=200)],
        render_kw={"placeholder": "Ex: Introdução à Teoria Musical"}
    )
    description = TextAreaField(
        "Descrição Curta (Objetivo da Aula)",
        validators=[Length(max=500)],
        render_kw={"rows": 3, "placeholder": "Uma breve descrição do que o aluno irá aprender nesta aula."}
    )
    module = StringField(
        "Módulo",
        validators=[Optional(), Length(max=120)],
        render_kw={"placeholder": "Ex: Fundamentos para Iniciantes"}
    )
    level = SelectField(
        "Nível",
        choices=[
            ("", "Não informado"),
            ("iniciante", "Iniciante"),
            ("basico", "Básico"),
            ("intermediario", "Intermediário"),
            ("avancado", "Avançado")
        ],
        validators=[Optional()]
    )
    estimated_minutes = IntegerField(
        "Duração estimada (min)",
        validators=[Optional()],
        render_kw={"placeholder": "Ex: 15"}
    )
    objectives = TextAreaField(
        "Objetivos",
        validators=[Optional()],
        render_kw={"rows": 4, "placeholder": "Um objetivo por linha."}
    )
    prerequisites = TextAreaField(
        "Pré-requisitos",
        validators=[Optional()],
        render_kw={"rows": 3, "placeholder": "Um pré-requisito por linha. Use 'Nenhum' para aulas iniciais."}
    )
    practice_focus = TextAreaField(
        "Foco da prática",
        validators=[Optional()],
        render_kw={"rows": 3, "placeholder": "Ex: Tocar notas limpas sem tensão por 5 minutos."}
    )
    order = IntegerField(
        "Ordem de Exibição",
        default=0,
        validators=[DataRequired()]
    )
    is_published = BooleanField(
        "Publicar esta aula?",
        default=False
    )
    submit = SubmitField("Salvar Aula")


class ResourceForm(FlaskForm):
    """Formulário para adicionar etapas (recursos) a uma aula."""
    title = StringField(
        "Título da Etapa",
        validators=[DataRequired(), Length(max=200)],
        render_kw={"placeholder": "Ex: Passo 1 - Posição das Mãos"}
    )
    content = HiddenField(
        "Texto Explicativo da Etapa (Parágrafo)",
        validators=[Optional()]
    )
    resource_type = SelectField(
        "Tipo de Mídia Associada",
        choices=[
            ("none", "Apenas Texto"),
            ("pdf", "Arquivo PDF (Partitura, Material)"),
            ("image", "Arquivo de Imagem (Diagrama, Acorde)"),
            ("youtube_url", "Vídeo do YouTube (Link)"),
            ("video_url", "Outro Vídeo (Link Direto)")
        ],
        validators=[DataRequired()],
        render_kw={'id': 'resourceTypeSelector'}
    )
    # Usado para uploads de arquivos
    file = FileField(
        "Arquivo de Mídia",
        validators=[Optional()]
    )
    # Usado para links externos
    url = StringField(
        "Link/URL do Vídeo",
        validators=[Optional()]
    )
    exercise_type = SelectField(
        "Exercício vinculado",
        choices=[
            ("", "Nenhum"),
            ("identify_note", "Identificar a Nota"),
            ("find_note", "Encontrar a Nota"),
            ("intervals", "Identificar Intervalo"),
            ("free_train", "Treino Livre"),
            ("harmonic_dictation", "Ditado Harmônico"),
            ("technical_drills", "Técnica e Aquecimento")
        ],
        validators=[Optional()]
    )
    exercise_params = TextAreaField(
        "Parâmetros do exercício (JSON)",
        validators=[Optional()],
        render_kw={"rows": 2, "placeholder": "{\"strings\":\"6,5\",\"frets\":\"0-12\"}"}
    )
    checklist_items = TextAreaField(
        "Checklist de conclusão",
        validators=[Optional()],
        render_kw={"rows": 3, "placeholder": "Um item por linha."}
    )
    submit = SubmitField("Adicionar Etapa")


class UserAdminForm(FlaskForm):
    """Formulário para um admin editar um usuário."""
    from app.guitar_study.models import UserRole
    
    role = SelectField(
        "Perfil",
        choices=[(role.value, role.name.title()) for role in UserRole],
        validators=[DataRequired()]
    )
    is_active = BooleanField("Usuário Ativo?")
    submit = SubmitField("Salvar Alterações")


class UserCreateForm(FlaskForm):
    """Formulário para o admin da escola criar um novo usuário (professor ou aluno)."""
    name = StringField(
        "Nome Completo",
        validators=[DataRequired(), Length(min=3, max=100)],
        render_kw={"placeholder": "Ex: João da Silva"}
    )
    username = StringField(
        "Nome de Usuário (Login)",
        validators=[DataRequired(), Length(min=3, max=50)],
        render_kw={"placeholder": "Ex: joao_guitar"}
    )
    email = StringField(
        "Endereço de Email",
        validators=[DataRequired(), Email(message="Formato de email inválido."), Length(max=100)],
        render_kw={"placeholder": "Ex: joao@escola.com"}
    )
    role = SelectField(
        "Perfil de Acesso",
        choices=[
            ("student", "Aluno"),
            ("teacher", "Professor")
        ],
        validators=[DataRequired()]
    )
    password = PasswordField(
        "Senha Inicial",
        validators=[DataRequired(), Length(min=6, max=50)],
        render_kw={"placeholder": "Mínimo de 6 caracteres"}
    )
    submit = SubmitField("Registrar Usuário")

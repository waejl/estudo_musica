import enum
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager

class School(db.Model):
    """Modelo para representar uma escola/inquilino na plataforma."""
    __tablename__ = "schools"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    users = db.relationship("User", back_populates="school")
    lessons = db.relationship("Lesson", back_populates="school")

    def __repr__(self):
        return f"<School {self.name}>"

class UserRole(enum.Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    SCHOOL_ADMIN = "school_admin"
    SUPER_ADMIN = "super_admin"

class User(db.Model, UserMixin):
    """Modelo para representar os usuários do sistema."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=True, index=True)
    
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.STUDENT, index=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = db.Column(db.DateTime, nullable=True)

    # Relacionamentos
    school = db.relationship("School", back_populates="users")
    settings = db.relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    custom_tunings = db.relationship("CustomTuning", back_populates="user", cascade="all, delete-orphan")
    favorites = db.relationship("Favorite", back_populates="user", cascade="all, delete-orphan")
    study_sessions = db.relationship("StudySession", back_populates="user", cascade="all, delete-orphan")
    exercise_attempts = db.relationship("ExerciseAttempt", back_populates="user", cascade="all, delete-orphan")
    study_goals = db.relationship("StudyGoal", back_populates="user", cascade="all, delete-orphan")
    recent_items = db.relationship("RecentItem", back_populates="user", cascade="all, delete-orphan")
    songs = db.relationship("Song", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password):
        """Gera e define o hash seguro da senha."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_super_admin(self):
        return self.role == UserRole.SUPER_ADMIN

    @property
    def is_school_admin(self):
        return self.role == UserRole.SCHOOL_ADMIN

    @property
    def is_teacher(self):
        return self.role == UserRole.TEACHER

    def __repr__(self):
        return f"<User {self.username}>"


class UserSettings(db.Model):
    """Modelo para representar as preferências do braço e sistema de cada usuário."""
    __tablename__ = "user_settings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    tuning_id = db.Column(db.String(50), default="standard", nullable=False)
    fret_count = db.Column(db.Integer, default=22, nullable=False)
    accidentals_preference = db.Column(db.String(10), default="sharps", nullable=False)  # sharps ou flats
    theme = db.Column(db.String(10), default="dark", nullable=False)  # dark ou light
    hand_orientation = db.Column(db.String(20), default="right_handed", nullable=False)  # right_handed ou left_handed

    # Relacionamento de volta para o usuário
    user = db.relationship("User", back_populates="settings")

    def __repr__(self):
        return f"<UserSettings user_id={self.user_id}>"


class CustomTuning(db.Model):
    """Modelo para afinações personalizadas cadastradas pelo usuário."""
    __tablename__ = "custom_tunings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.String(100), nullable=False)  # Ex: "C G C F A D"
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relacionamento
    user = db.relationship("User", back_populates="custom_tunings")

    def __repr__(self):
        return f"<CustomTuning name={self.name} user_id={self.user_id}>"


class Favorite(db.Model):
    """Modelo para gerenciar itens favoritados (escalas, modos, acordes)."""
    __tablename__ = "favorites"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # scale, mode, chord
    item_key = db.Column(db.String(100), nullable=False)  # Ex: "C_major", "A_dorian", "G_major_7"
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relacionamento
    user = db.relationship("User", back_populates="favorites")

    def __repr__(self):
        return f"<Favorite {self.category}:{self.item_key} user_id={self.user_id}>"


class StudySession(db.Model):
    """Modelo para rastreamento de sessões de estudo realizadas pelo usuário."""
    __tablename__ = "study_sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # fretboard, scale, mode, chord, exercise
    item_key = db.Column(db.String(100), nullable=False)  # Ex: "major_scale", "identify_note"
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relacionamento
    user = db.relationship("User", back_populates="study_sessions")

    def __repr__(self):
        return f"<StudySession category={self.category} duration={self.duration_minutes}m>"


class ExerciseAttempt(db.Model):
    """Modelo para armazenar o resultado de tentativas em exercícios interativos."""
    __tablename__ = "exercise_attempts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    exercise_type = db.Column(db.String(50), nullable=False)  # identify_note, find_note, intervals, scales, modes
    questions_count = db.Column(db.Integer, nullable=False)
    correct_count = db.Column(db.Integer, nullable=False)
    incorrect_count = db.Column(db.Integer, nullable=False)
    score_percentage = db.Column(db.Float, nullable=False)
    time_spent_seconds = db.Column(db.Integer, nullable=False)
    difficulty = db.Column(db.String(20), default="medium", nullable=False)  # easy, medium, hard
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relacionamento
    user = db.relationship("User", back_populates="exercise_attempts")

    def __repr__(self):
        return f"<ExerciseAttempt type={self.exercise_type} score={self.score_percentage}%>"


class StudyGoal(db.Model):
    """Modelo para as metas de estudos do usuário."""
    __tablename__ = "study_goals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    target_minutes = db.Column(db.Integer, nullable=False)
    current_minutes = db.Column(db.Integer, default=0, nullable=False)
    is_completed = db.Column(db.Boolean, default=False, nullable=False)
    deadline = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relacionamento
    user = db.relationship("User", back_populates="study_goals")

    def __repr__(self):
        return f"<StudyGoal title={self.title} completed={self.is_completed}>"


class RecentItem(db.Model):
    """Modelo para rastrear acessos recentes e preencher o dashboard com facilidade."""
    __tablename__ = "recent_items"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # scale, mode, chord
    item_key = db.Column(db.String(100), nullable=False)
    last_accessed_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relacionamento
    user = db.relationship("User", back_populates="recent_items")

    def __repr__(self):
        return f"<RecentItem category={self.category} item={self.item_key}>"


class Song(db.Model):
    """Modelo para cifras e músicas salvas pelo usuário."""
    __tablename__ = "songs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    artist = db.Column(db.String(200), nullable=False)
    genre = db.Column(db.String(50), default="outros", nullable=False)
    content = db.Column(db.Text, nullable=False)
    capo = db.Column(db.Integer, default=0, nullable=False)
    source_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="songs")

    def __repr__(self):
        return f"<Song {self.artist} - {self.title}>"


class Lesson(db.Model):
    """
    Modelo para aulas.
    Aulas base (do superadmin) não têm school_id.
    Aulas customizadas (de uma escola) têm school_id.
    """
    __tablename__ = "lessons"

    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=True, index=True)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=True)
    order = db.Column(db.Integer, nullable=False, default=0)
    is_published = db.Column(db.Boolean, default=False, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    school = db.relationship("School", back_populates="lessons")
    resources = db.relationship("LessonResource", back_populates="lesson", cascade="all, delete-orphan", lazy='dynamic')

    def __repr__(self):
        return f"<Lesson {self.title}>"


class LessonResource(db.Model):
    """Modelo para as Etapas (Passos) associadas a uma aula."""
    __tablename__ = "lesson_resources"

    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Tipo do recurso principal da etapa: 'pdf', 'image', 'video_url', 'youtube_url' ou 'none' se for apenas texto
    resource_type = db.Column(db.String(50), nullable=True, default='none')
    
    # Caminho para o arquivo, URL ou JSON do braço de guitarra
    path = db.Column(db.String(500), nullable=True)
    
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=True) # Texto explicativo rico da etapa
    order = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    lesson = db.relationship("Lesson", back_populates="resources")
    
    # Suporte a múltiplos arquivos/links adicionais para a mesma etapa
    media_items = db.relationship("StepMedia", back_populates="resource", cascade="all, delete-orphan", lazy='dynamic')

    def __repr__(self):
        return f"<LessonResource {self.title} (type={self.resource_type})>"


class StepMedia(db.Model):
    """Modelo para múltiplos arquivos/mídias adicionais atrelados a uma única etapa."""
    __tablename__ = "step_medias"

    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey("lesson_resources.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title = db.Column(db.String(200), nullable=True) # Legenda/título do arquivo individual
    media_type = db.Column(db.String(50), nullable=False) # 'pdf', 'image', 'youtube_url', 'video_url', 'fretboard'
    path = db.Column(db.String(500), nullable=False) # Caminho físico, URL ou JSON das notas marcadas no braço
    order = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    resource = db.relationship("LessonResource", back_populates="media_items")

    def __repr__(self):
        return f"<StepMedia {self.media_type} path={self.path}>"


# Loader para o Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

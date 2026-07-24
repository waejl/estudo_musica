from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy import func
from app.extensions import db
from app.guitar_study import guitar_study
from app.guitar_study.models import (
    UserSettings, Favorite, StudySession, ExerciseAttempt, StudyGoal, RecentItem, Song
)
from app.guitar_study.services.music_theory import TUNINGS, SHARPS_SCALE

@guitar_study.route("/")
@guitar_study.route("/dashboard")
@login_required
def dashboard():
    """Painel principal do usuário logado (Dashboard)."""
    user_id = current_user.id
    
    # 1. Total de sessões e tempo total
    stats = db.session.query(
        func.count(StudySession.id),
        func.sum(StudySession.duration_minutes)
    ).filter_by(user_id=user_id).first()
    
    total_sessions = stats[0] or 0
    total_duration = stats[1] or 0
    
    # 2. Último estudo realizado
    last_session = StudySession.query.filter_by(user_id=user_id).order_by(StudySession.created_at.desc()).first()
    
    # 3. Item mais estudado (escala e modo)
    most_studied_scale_row = db.session.query(
        StudySession.item_key, func.count(StudySession.id)
    ).filter_by(user_id=user_id, category="scale").group_by(StudySession.item_key).order_by(func.count(StudySession.id).desc()).first()
    
    most_studied_mode_row = db.session.query(
        StudySession.item_key, func.count(StudySession.id)
    ).filter_by(user_id=user_id, category="mode").group_by(StudySession.item_key).order_by(func.count(StudySession.id).desc()).first()
    
    most_studied_scale = most_studied_scale_row[0].replace("_", " ").title() if most_studied_scale_row else "Nenhuma escala ainda"
    most_studied_mode = most_studied_mode_row[0].replace("_", " ").title() if most_studied_mode_row else "Nenhum modo ainda"
    
    # 4. Sequência de dias estudados (Streak)
    # Busca todas as datas distintas em que houve estudo
    session_dates = db.session.query(
        func.date(StudySession.created_at)
    ).filter_by(user_id=user_id).distinct().order_by(func.date(StudySession.created_at).desc()).all()
    
    streak = 0
    if session_dates:
        dates_set = {r[0] for r in session_dates}
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)
        
        # O streak começa se o usuário estudou hoje ou ontem
        current_date = today if today in dates_set else (yesterday if yesterday in dates_set else None)
        
        if current_date:
            streak = 1
            check_date = current_date - timedelta(days=1)
            while check_date in dates_set:
                streak += 1
                check_date -= timedelta(days=1)
                
    # 5. Últimos itens favoritados
    favorites = Favorite.query.filter_by(user_id=user_id).order_by(Favorite.created_at.desc()).limit(5).all()
    
    # 6. Progresso Semanal (Sessões dos últimos 7 dias)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    weekly_sessions_count = StudySession.query.filter(
        StudySession.user_id == user_id,
        StudySession.created_at >= seven_days_ago
    ).count()
    
    # 7. Metas de estudos
    goals = StudyGoal.query.filter_by(user_id=user_id).order_by(StudyGoal.is_completed.asc(), StudyGoal.deadline.asc()).limit(3).all()
    
    # 8. Recomendações (Dinâmicas simplificadas baseadas no que já foi estudado)
    recommendations = []
    if total_sessions == 0:
        recommendations.append({
            "title": "Conheça as notas no Braço",
            "desc": "Comece clicando em notas soltas na guitarra para memorizar suas posições naturais.",
            "url": url_for("guitar_study.fretboard")
        })
        recommendations.append({
            "title": "A Escala Pentatônica Menor",
            "desc": "Esta é a escala de entrada mais importante. Estude em Lá menor (Am).",
            "url": url_for("guitar_study.scales") + "?root=A&type=pentatonic_minor"
        })
    else:
        recommendations.append({
            "title": "Estude o Modo Dórico",
            "desc": "Quer um tempero jazzístico? Pratique a sonoridade misteriosa do Modo Dórico.",
            "url": url_for("guitar_study.modes") + "?root=A&type=dorian"
        })
        recommendations.append({
            "title": "Exercício de Identificar Notas",
            "desc": "Melhore sua velocidade de leitura encontrando notas aleatórias sob pressão.",
            "url": url_for("guitar_study.exercises") + "?type=identify_note"
        })

    return render_template(
        "guitar_study/dashboard.html",
        total_sessions=total_sessions,
        total_duration=total_duration,
        last_session=last_session,
        most_studied_scale=most_studied_scale,
        most_studied_mode=most_studied_mode,
        streak=streak,
        favorites=favorites,
        weekly_sessions_count=weekly_sessions_count,
        goals=goals,
        recommendations=recommendations
    )


@guitar_study.route("/fretboard")
@login_required
def fretboard():
    """Visualização interativa do braço da guitarra."""
    settings = current_user.settings
    tunings = TUNINGS
    
    # Busca afinações personalizadas do usuário
    from app.guitar_study.models import CustomTuning
    custom_tunings = CustomTuning.query.filter_by(user_id=current_user.id).all()
    
    return render_template(
        "guitar_study/fretboard.html",
        settings=settings,
        tunings=tunings,
        custom_tunings=custom_tunings,
        chromatic_notes=SHARPS_SCALE
    )


@guitar_study.route("/scales")
@login_required
def scales():
    """Visualização e estudo de escalas musicais."""
    settings = current_user.settings
    return render_template(
        "guitar_study/scales.html",
        settings=settings,
        chromatic_notes=SHARPS_SCALE
    )


@guitar_study.route("/modes")
@login_required
def modes():
    """Visualização, estudo e comparação de modos gregos."""
    settings = current_user.settings
    return render_template(
        "guitar_study/modes.html",
        settings=settings,
        chromatic_notes=SHARPS_SCALE
    )


@guitar_study.route("/chords")
@login_required
def chords():
    """Visualização, formação e diagrama de acordes."""
    settings = current_user.settings
    return render_template(
        "guitar_study/chords.html",
        settings=settings,
        chromatic_notes=SHARPS_SCALE
    )


@guitar_study.route("/exercises")
@login_required
def exercises():
    """Página de exercícios práticos interativos."""
    settings = current_user.settings
    return render_template("guitar_study/exercises.html", settings=settings)


@guitar_study.route("/songs")
@login_required
def songs():
    """Lista de cifras salvas pelo usuário."""
    genre_filter = request.args.get("genre", "")
    query = Song.query.filter_by(user_id=current_user.id)
    if genre_filter:
        query = query.filter_by(genre=genre_filter)
    all_songs = query.order_by(Song.artist.asc(), Song.title.asc()).all()
    genres = [
        ("rock", "Rock Nacional"),
        ("mpb", "MPB"),
        ("rock_internacional", "Rock Internacional"),
        ("metal", "Metal"),
        ("evangelica", "Evangélica"),
        ("outros", "Outros"),
    ]
    return render_template(
        "guitar_study/songs.html",
        songs=all_songs,
        genres=genres,
        genre_filter=genre_filter
    )


@guitar_study.route("/songs/<int:song_id>")
@login_required
def song_view(song_id):
    """Visualizador de cifra individual."""
    song = Song.query.filter_by(id=song_id, user_id=current_user.id).first_or_404()
    return render_template("guitar_study/song_view.html", song=song)


@guitar_study.route("/harmony")
@login_required
def harmony():
    """Página de estudo de harmonia funcional, campo harmônico e preparações."""
    settings = current_user.settings
    return render_template(
        "guitar_study/harmony.html",
        settings=settings,
        chromatic_notes=SHARPS_SCALE
    )


@guitar_study.route("/settings")
@login_required
def settings():
    """Configurações pessoais, de afinação e tema."""
    settings = current_user.settings
    tunings = TUNINGS
    
    # Busca afinações personalizadas
    from app.guitar_study.models import CustomTuning
    custom_tunings = CustomTuning.query.filter_by(user_id=current_user.id).all()
    
    return render_template(
        "guitar_study/settings.html",
        settings=settings,
        tunings=tunings,
        custom_tunings=custom_tunings
    )

from datetime import datetime, date
from flask import jsonify, request, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.guitar_study import guitar_study
from app.guitar_study.models import (
    UserSettings, CustomTuning, Favorite, StudySession,
    ExerciseAttempt, StudyGoal, RecentItem, Song
)
from app.guitar_study.services.music_theory import MusicTheoryService, TUNINGS

def get_user_tuning_notes(user_id: int, tuning_id: str) -> list:
    """Busca as notas das cordas soltas com base no ID da afinação."""
    if tuning_id in TUNINGS:
        return TUNINGS[tuning_id]["notes"]
        
    # Se não for padrão, busca no banco por personalizada
    custom = CustomTuning.query.filter_by(user_id=user_id, id=tuning_id).first()
    if custom:
        return custom.notes.split()
        
    # Fallback para Standard
    return TUNINGS["standard"]["notes"]


# =====================================================================
# API: NOTAS
# =====================================================================
@guitar_study.route("/api/v1/notes", methods=["GET"])
def api_get_notes():
    """Retorna as 12 notas cromáticas conforme preferência (sharps/flats)."""
    pref = request.args.get("preference", "sharps")
    if pref not in ["sharps", "flats"]:
        pref = "sharps"
        
    try:
        notes = MusicTheoryService.get_chromatic_scale(pref)
        return jsonify({
            "success": True,
            "data": {
                "notes": notes,
                "preference": pref
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {
                "code": "SERVER_ERROR",
                "message": f"Erro ao buscar notas cromáticas: {str(e)}"
            }
        }), 500


# =====================================================================
# API: BRAÇO DA GUITARRA (FRETBOARD)
# =====================================================================
@guitar_study.route("/api/v1/fretboard", methods=["GET"])
@login_required
def api_get_fretboard():
    """Retorna o mapeamento completo de notas no braço da guitarra."""
    settings = current_user.settings
    tuning_id = request.args.get("tuning_id", settings.tuning_id if settings else "standard")
    frets = int(request.args.get("fret_count", settings.fret_count if settings else 22))
    pref = request.args.get("preference", settings.accidentals_preference if settings else "sharps")
    
    if frets not in [12, 15, 21, 22, 24]:
        frets = 22
    if pref not in ["sharps", "flats"]:
        pref = "sharps"
        
    try:
        string_notes = get_user_tuning_notes(current_user.id, tuning_id)
        
        # Garante que as cordas sejam servidas do topo (1ª corda aguda) para a base (6ª corda grave)
        # Se as notas começarem por E e A (grave), nós as invertemos para que a aguda fique no índice 0
        if len(string_notes) == 6 and string_notes[0].upper() in ["E", "D", "C"] and string_notes[1].upper() in ["A", "G"]:
            string_notes = list(reversed(string_notes))
            
        # Gera o braço dinamicamente
        fretboard_data = []
        # Percorremos as cordas de cima para baixo (da 1ª mais aguda até a 6ª mais grave)
        # Convenção: Corda 1 (E aguda) a Corda 6 (E grave)
        for string_idx, open_note in enumerate(string_notes):
            string_fret_notes = []
            for fret in range(frets + 1):  # Casa 0 até a quantidade de casas
                note_name = MusicTheoryService.get_note_by_fret(open_note, fret, pref)
                frequency = MusicTheoryService.get_frequency_for_fret(open_note, fret, string_idx)
                string_fret_notes.append({
                    "fret": fret,
                    "note": note_name,
                    "frequency": frequency
                })
            fretboard_data.append({
                "string_index": string_idx + 1,
                "open_note": open_note,
                "frets": string_fret_notes
            })
            
        return jsonify({
            "success": True,
            "data": {
                "tuning_id": tuning_id,
                "fret_count": frets,
                "preference": pref,
                "strings": fretboard_data
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {
                "code": "FRETBOARD_ERROR",
                "message": f"Não foi possível calcular o braço da guitarra: {str(e)}"
            }
        }), 500


# =====================================================================
# API: ESCALAS
# =====================================================================
@guitar_study.route("/api/v1/scales", methods=["GET"])
def api_get_scales():
    """Retorna notas, intervalos e fórmula de uma escala."""
    root = request.args.get("root", "C").strip()
    scale_type = request.args.get("type", "major").strip()
    pref = request.args.get("preference", "sharps")
    
    try:
        scale_info = MusicTheoryService.get_scale_notes_and_intervals(root, scale_type, pref)
        
        # Registrar o item acessado se estiver logado
        if current_user.is_authenticated:
            register_recent_item(current_user.id, "scale", f"{root}_{scale_type}")
            
        return jsonify({
            "success": True,
            "data": scale_info
        })
    except ValueError as ve:
        return jsonify({
            "success": False,
            "error": {
                "code": "INVALID_PARAMETER",
                "message": str(ve)
            }
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {
                "code": "SERVER_ERROR",
                "message": f"Erro ao calcular dados da escala: {str(e)}"
            }
        }), 500


# =====================================================================
# API: MODOS GREGOS
# =====================================================================
@guitar_study.route("/api/v1/modes", methods=["GET"])
def api_get_modes():
    """Retorna notas, intervalos e características de um Modo Grego."""
    root = request.args.get("root", "A").strip()
    mode_type = request.args.get("type", "dorian").strip()
    pref = request.args.get("preference", "sharps")
    
    try:
        mode_info = MusicTheoryService.get_mode_notes_and_intervals(root, mode_type, pref)
        
        # Registrar o item acessado se estiver logado
        if current_user.is_authenticated:
            register_recent_item(current_user.id, "mode", f"{root}_{mode_type}")
            
        return jsonify({
            "success": True,
            "data": mode_info
        })
    except ValueError as ve:
        return jsonify({
            "success": False,
            "error": {
                "code": "INVALID_PARAMETER",
                "message": str(ve)
            }
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {
                "code": "SERVER_ERROR",
                "message": f"Erro ao calcular dados do modo: {str(e)}"
            }
        }), 500


# =====================================================================
# API: ACORDES
# =====================================================================
@guitar_study.route("/api/v1/chords", methods=["GET"])
def api_get_chords():
    """Retorna notas, intervalos e CAGED de um Acorde."""
    root = request.args.get("root", "C").strip()
    chord_type = request.args.get("type", "major").strip()
    pref = request.args.get("preference", "sharps")
    
    try:
        chord_info = MusicTheoryService.get_chord_notes_and_intervals(root, chord_type, pref)
        
        # Registrar o item acessado se estiver logado
        if current_user.is_authenticated:
            register_recent_item(current_user.id, "chord", f"{root}_{chord_type}")
            
        return jsonify({
            "success": True,
            "data": chord_info
        })
    except ValueError as ve:
        return jsonify({
            "success": False,
            "error": {
                "code": "INVALID_PARAMETER",
                "message": str(ve)
            }
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {
                "code": "SERVER_ERROR",
                "message": f"Erro ao calcular dados do acorde: {str(e)}"
            }
        }), 500


@guitar_study.route("/api/v1/chords/voicings", methods=["GET"])
@login_required
def api_get_chord_voicings():
    """Gera e retorna todos os voicings humanamente possíveis de um acorde."""
    root = request.args.get("root", "C").strip()
    chord_type = request.args.get("type", "major").strip()
    pref = request.args.get("preference", "sharps")
    
    settings = current_user.settings
    tuning_id = request.args.get("tuning_id", settings.tuning_id if settings else "standard")
    fret_count = int(request.args.get("fret_count", settings.fret_count if settings else 12))

    try:
        # 1. Obter as notas do acorde
        chord_info = MusicTheoryService.get_chord_notes_and_intervals(root, chord_type, pref)
        chord_notes = chord_info["notes"]
        
        # 2. Obter a afinação
        tuning_notes = get_user_tuning_notes(current_user.id, tuning_id)
        # O serviço espera a afinação da corda mais aguda (1) para a mais grave (6)
        # Invertemos se estiver no formato EADGBE
        if len(tuning_notes) == 6 and tuning_notes[0].upper() in ["E", "D", "C"] and tuning_notes[1].upper() in ["A", "G"]:
            tuning_notes = list(reversed(tuning_notes))

        # 3. Gerar os voicings
        all_voicings = MusicTheoryService.get_all_voicings(
            chord_notes=chord_notes,
            root_note=root,
            tuning_notes=tuning_notes,
            fret_count=fret_count,
            preference=pref
        )
        
        return jsonify({
            "success": True,
            "data": {
                "root": root,
                "chord_type": chord_type,
                "voicings": all_voicings
            }
        })
    except ValueError as ve:
        return jsonify({
            "success": False,
            "error": {"code": "INVALID_PARAMETER", "message": str(ve)}
        }), 400
    except Exception as e:
        current_app.logger.error(f"Erro ao gerar voicings para {root} {chord_type}: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": {"code": "SERVER_ERROR", "message": f"Erro ao gerar voicings: {str(e)}"}
        }), 500


# =====================================================================
# API: SESSÕES DE ESTUDO (STUDY SESSIONS)
# =====================================================================
@guitar_study.route("/api/v1/study-sessions", methods=["GET", "POST"])
@login_required
def api_study_sessions():
    """Lista ou registra sessões de estudo do usuário."""
    if request.method == "POST":
        data = request.get_json() or {}
        category = data.get("category", "").strip()
        item_key = data.get("item_key", "").strip()
        duration = data.get("duration_minutes")
        notes = data.get("notes", "").strip()
        
        if not category or not item_key or duration is None:
            return jsonify({
                "success": False,
                "error": {
                    "code": "MISSING_FIELDS",
                    "message": "Os campos 'category', 'item_key' e 'duration_minutes' são obrigatórios."
                }
            }), 400
            
        try:
            duration = int(duration)
            if duration <= 0:
                raise ValueError()
        except ValueError:
            return jsonify({
                "success": False,
                "error": {
                    "code": "INVALID_DURATION",
                    "message": "A duração em minutos deve ser um número inteiro maior que zero."
                }
            }), 400
            
        try:
            # Salva a sessão no banco
            session = StudySession(
                user_id=current_user.id,
                category=category,
                item_key=item_key,
                duration_minutes=duration,
                notes=notes
            )
            db.session.add(session)
            
            # Atualiza metas de estudos relacionadas ao usuário se existirem
            update_goals_minutes(current_user.id, duration)
            
            db.session.commit()
            
            current_app.logger.info(f"Sessão de estudo registrada para {current_user.username}: {category} ({duration} min)")
            
            return jsonify({
                "success": True,
                "data": {
                    "id": session.id,
                    "category": session.category,
                    "item_key": session.item_key,
                    "duration_minutes": session.duration_minutes,
                    "created_at": session.created_at.isoformat()
                }
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "success": False,
                "error": {
                    "code": "DATABASE_ERROR",
                    "message": f"Erro ao registrar sessão de estudos: {str(e)}"
                }
            }), 500
            
    # GET: Lista histórico recente de estudos
    try:
        limit = int(request.args.get("limit", 10))
        sessions = StudySession.query.filter_by(user_id=current_user.id).order_by(StudySession.created_at.desc()).limit(limit).all()
        
        serialized = []
        for s in sessions:
            serialized.append({
                "id": s.id,
                "category": s.category,
                "item_key": s.item_key,
                "duration_minutes": s.duration_minutes,
                "notes": s.notes,
                "created_at": s.created_at.isoformat()
            })
            
        return jsonify({
            "success": True,
            "data": {
                "sessions": serialized
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {
                "code": "SERVER_ERROR",
                "message": f"Erro ao carregar sessões de estudo: {str(e)}"
            }
        }), 500


# =====================================================================
# API: FAVORITOS (FAVORITES)
# =====================================================================
@guitar_study.route("/api/v1/favorites", methods=["GET", "POST", "DELETE"])
@login_required
def api_favorites():
    """Gerencia itens favoritados do usuário."""
    if request.method == "POST":
        data = request.get_json() or {}
        category = data.get("category", "").strip()
        item_key = data.get("item_key", "").strip()
        
        if not category or not item_key:
            return jsonify({
                "success": False,
                "error": {
                    "code": "MISSING_FIELDS",
                    "message": "Os campos 'category' e 'item_key' são obrigatórios."
                }
            }), 400
            
        # Verifica se já está favoritado
        existing = Favorite.query.filter_by(user_id=current_user.id, category=category, item_key=item_key).first()
        if existing:
            return jsonify({
                "success": True,
                "message": "Este item já está nos favoritos.",
                "data": {"id": existing.id}
            })
            
        try:
            fav = Favorite(user_id=current_user.id, category=category, item_key=item_key)
            db.session.add(fav)
            db.session.commit()
            return jsonify({
                "success": True,
                "data": {
                    "id": fav.id,
                    "category": fav.category,
                    "item_key": fav.item_key
                }
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "success": False,
                "error": {
                    "code": "DATABASE_ERROR",
                    "message": f"Erro ao favoritar item: {str(e)}"
                }
            }), 500
            
    if request.method == "DELETE":
        data = request.get_json() or {}
        category = data.get("category", "").strip()
        item_key = data.get("item_key", "").strip()
        
        if not category or not item_key:
            return jsonify({
                "success": False,
                "error": {
                    "code": "MISSING_FIELDS",
                    "message": "Os campos 'category' e 'item_key' são obrigatórios."
                }
            }), 400
            
        fav = Favorite.query.filter_by(user_id=current_user.id, category=category, item_key=item_key).first()
        if not fav:
            return jsonify({
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Este item não foi encontrado nos favoritos."
                }
            }), 404
            
        try:
            db.session.delete(fav)
            db.session.commit()
            return jsonify({
                "success": True,
                "message": "Item removido dos favoritos com sucesso."
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "success": False,
                "error": {
                    "code": "DATABASE_ERROR",
                    "message": f"Erro ao remover favorito: {str(e)}"
                }
            }), 500
            
    # GET: Lista favoritos do usuário
    try:
        favs = Favorite.query.filter_by(user_id=current_user.id).order_by(Favorite.created_at.desc()).all()
        serialized = [{
            "id": f.id,
            "category": f.category,
            "item_key": f.item_key,
            "created_at": f.created_at.isoformat()
        } for f in favs]
        
        return jsonify({
            "success": True,
            "data": {
                "favorites": serialized
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {
                "code": "SERVER_ERROR",
                "message": f"Erro ao carregar favoritos: {str(e)}"
            }
        }), 500


# =====================================================================
# API: TENTATIVAS DE EXERCÍCIOS (EXERCISES)
# =====================================================================
@guitar_study.route("/api/v1/exercises", methods=["GET", "POST"])
@login_required
def api_exercises():
    """Lista ou registra tentativas de exercícios do usuário."""
    if request.method == "POST":
        data = request.get_json() or {}
        exercise_type = data.get("exercise_type", "").strip()
        questions_count = data.get("questions_count")
        correct_count = data.get("correct_count")
        incorrect_count = data.get("incorrect_count")
        time_spent_seconds = data.get("time_spent_seconds")
        difficulty = data.get("difficulty", "medium").strip()
        
        if not exercise_type or questions_count is None or correct_count is None or incorrect_count is None or time_spent_seconds is None:
            return jsonify({
                "success": False,
                "error": {
                    "code": "MISSING_FIELDS",
                    "message": "Parâmetros obrigatórios ausentes."
                }
            }), 400
            
        try:
            questions = int(questions_count)
            correct = int(correct_count)
            incorrect = int(incorrect_count)
            time_spent = int(time_spent_seconds)
            
            if questions <= 0 or correct < 0 or incorrect < 0 or time_spent < 0:
                raise ValueError()
        except ValueError:
            return jsonify({
                "success": False,
                "error": {
                    "code": "INVALID_FIELDS",
                    "message": "Valores numéricos inválidos."
                }
            }), 400
            
        score = round((correct / questions) * 100, 2)
        
        try:
            attempt = ExerciseAttempt(
                user_id=current_user.id,
                exercise_type=exercise_type,
                questions_count=questions,
                correct_count=correct,
                incorrect_count=incorrect,
                score_percentage=score,
                time_spent_seconds=time_spent,
                difficulty=difficulty
            )
            db.session.add(attempt)
            db.session.commit()
            
            current_app.logger.info(f"Exercício registrado para {current_user.username}: {exercise_type} ({score}%)")
            
            return jsonify({
                "success": True,
                "data": {
                    "id": attempt.id,
                    "score_percentage": attempt.score_percentage,
                    "created_at": attempt.created_at.isoformat()
                }
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "success": False,
                "error": {
                    "code": "DATABASE_ERROR",
                    "message": f"Erro ao registrar exercício: {str(e)}"
                }
            }), 500
            
    # GET: Retorna estatísticas de exercícios do usuário
    try:
        attempts = ExerciseAttempt.query.filter_by(user_id=current_user.id).order_by(ExerciseAttempt.created_at.desc()).all()
        
        serialized = [{
            "id": a.id,
            "exercise_type": a.exercise_type,
            "questions_count": a.questions_count,
            "correct_count": a.correct_count,
            "incorrect_count": a.incorrect_count,
            "score_percentage": a.score_percentage,
            "time_spent_seconds": a.time_spent_seconds,
            "difficulty": a.difficulty,
            "created_at": a.created_at.isoformat()
        } for a in attempts]
        
        return jsonify({
            "success": True,
            "data": {
                "attempts": serialized
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {
                "code": "SERVER_ERROR",
                "message": f"Erro ao carregar histórico de exercícios: {str(e)}"
            }
        }), 500


# =====================================================================
# API: CONFIGURAÇÕES (SETTINGS)
# =====================================================================
@guitar_study.route("/api/v1/settings", methods=["GET"])
@login_required
def api_get_settings():
    """Retorna as configurações do usuário atual."""
    settings = current_user.settings
    if not settings:
        return jsonify({
            "success": False,
            "error": {
                "code": "NOT_FOUND",
                "message": "Configurações não encontradas."
            }
        }), 404
        
    return jsonify({
        "success": True,
        "data": {
            "tuning_id": settings.tuning_id,
            "fret_count": settings.fret_count,
            "accidentals_preference": settings.accidentals_preference,
            "theme": settings.theme,
            "hand_orientation": settings.hand_orientation
        }
    })


# =====================================================================
# API: CIFRAS (SONGS)
# =====================================================================
VALID_GENRES = {"rock", "mpb", "rock_internacional", "metal", "evangelica", "outros"}

@guitar_study.route("/api/v1/songs", methods=["POST"])
@login_required
def api_create_song():
    """Cria uma nova cifra para o usuário logado."""
    data = request.get_json() or {}
    title = (data.get("title") or "").strip()
    artist = (data.get("artist") or "").strip()
    genre = (data.get("genre") or "outros").strip()
    content = (data.get("content") or "").strip()
    capo = data.get("capo", 0)
    source_url = (data.get("source_url") or "").strip() or None

    if not title or not artist or not content:
        return jsonify({
            "success": False,
            "error": {"code": "MISSING_FIELDS", "message": "Título, artista e cifra são obrigatórios."}
        }), 400

    if genre not in VALID_GENRES:
        genre = "outros"

    try:
        capo = int(capo)
        if capo < 0 or capo > 12:
            capo = 0
    except (ValueError, TypeError):
        capo = 0

    try:
        song = Song(
            user_id=current_user.id,
            title=title,
            artist=artist,
            genre=genre,
            content=content,
            capo=capo,
            source_url=source_url
        )
        db.session.add(song)
        db.session.commit()

        current_app.logger.info(f"Cifra criada por {current_user.username}: {artist} - {title}")

        return jsonify({
            "success": True,
            "data": {
                "id": song.id,
                "title": song.title,
                "artist": song.artist,
                "genre": song.genre,
                "capo": song.capo,
                "created_at": song.created_at.isoformat()
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": {"code": "DATABASE_ERROR", "message": f"Erro ao salvar cifra: {str(e)}"}
        }), 500


@guitar_study.route("/api/v1/songs/<int:song_id>", methods=["DELETE"])
@login_required
def api_delete_song(song_id):
    """Remove uma cifra do usuário logado."""
    song = Song.query.filter_by(id=song_id, user_id=current_user.id).first()
    if not song:
        return jsonify({
            "success": False,
            "error": {"code": "NOT_FOUND", "message": "Cifra não encontrada."}
        }), 404

    try:
        db.session.delete(song)
        db.session.commit()
        return jsonify({"success": True, "message": "Cifra removida com sucesso."})
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": {"code": "DATABASE_ERROR", "message": f"Erro ao remover cifra: {str(e)}"}
        }), 500


# =====================================================================
# MÉTODOS AUXILIARES PRIVADOS
# =====================================================================
def register_recent_item(user_id: int, category: str, item_key: str):
    """Auxiliar para gerenciar a lista de acessos recentes (Dashboard)."""
    try:
        # Tenta buscar se já foi acessado recentemente
        recent = RecentItem.query.filter_by(user_id=user_id, category=category, item_key=item_key).first()
        if recent:
            recent.last_accessed_at = datetime.utcnow()
        else:
            # Cria novo registro
            recent = RecentItem(user_id=user_id, category=category, item_key=item_key)
            db.session.add(recent)
            
            # Limita a 5 itens recentes no máximo para não sobrecarregar
            all_recents = RecentItem.query.filter_by(user_id=user_id).order_by(RecentItem.last_accessed_at.desc()).all()
            if len(all_recents) >= 5:
                # Remove os mais antigos excedentes
                for r_old in all_recents[4:]:
                    db.session.delete(r_old)
                    
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao registrar item recente: {str(e)}")


def update_goals_minutes(user_id: int, minutes: int):
    """Atualiza as metas de estudo ativas do usuário adicionando minutos estudados."""
    try:
        goals = StudyGoal.query.filter_by(user_id=user_id, is_completed=False).all()
        for g in goals:
            g.current_minutes += minutes
            if g.current_minutes >= g.target_minutes:
                g.current_minutes = g.target_minutes
                g.is_completed = True
        # Observação: O commit é executado no chamador principal que gerencia a sessão de estudos.
    except Exception as e:
        current_app.logger.error(f"Erro ao atualizar progresso de metas de estudo: {str(e)}")


# =====================================================================
# API: HARMONIA (HARMONY)
# =====================================================================
@guitar_study.route("/api/v1/harmony", methods=["GET"])
@login_required
def api_get_harmony():
    """Retorna os dados do Campo Harmônico e preparações para o tom selecionado."""
    root = request.args.get("root", "C").strip()
    scale_type = request.args.get("type", "major").strip()
    pref = request.args.get("preference", "sharps")
    
    try:
        harmony_info = MusicTheoryService.get_harmony_info(root, scale_type, pref)
        
        # Registrar como item recente
        register_recent_item(current_user.id, "scale", f"{root}_{scale_type}_harmony")
        
        return jsonify({
            "success": True,
            "data": harmony_info
        })
    except ValueError as ve:
        return jsonify({
            "success": False,
            "error": {"code": "INVALID_PARAMETER", "message": str(ve)}
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {"code": "SERVER_ERROR", "message": f"Erro ao calcular dados de harmonia: {str(e)}"}
        }), 500

from datetime import datetime

from app.extensions import db
from app.guitar_study.models import Lesson, LessonProgress, LessonResource


def get_published_lessons():
    return Lesson.query.filter_by(is_published=True).order_by(Lesson.order.asc(), Lesson.id.asc()).all()


def get_progress_map(user_id):
    progress_rows = LessonProgress.query.filter_by(user_id=user_id).all()
    return {row.lesson_id: row for row in progress_rows}


def get_or_create_progress(user_id, lesson):
    progress = LessonProgress.query.filter_by(user_id=user_id, lesson_id=lesson.id).first()
    if progress:
        return progress

    first_resource = lesson.resources.order_by(LessonResource.order.asc()).first()
    progress = LessonProgress(
        user_id=user_id,
        lesson_id=lesson.id,
        current_resource_id=first_resource.id if first_resource else None,
        status="in_progress",
    )
    progress.set_completed_ids([])
    progress.set_checklist_state({})
    db.session.add(progress)
    db.session.commit()
    return progress


def recommendation_for_user(user_id):
    lessons = get_published_lessons()
    progress_map = get_progress_map(user_id)

    for lesson in lessons:
        progress = progress_map.get(lesson.id)
        if progress and progress.status == "in_progress":
            return {
                "kind": "continue",
                "lesson": lesson,
                "progress": progress,
                "title": "Continue sua aula",
                "description": "Retome exatamente de onde parou.",
            }

    for lesson in lessons:
        progress = progress_map.get(lesson.id)
        if not progress or progress.status != "completed":
            return {
                "kind": "start",
                "lesson": lesson,
                "progress": progress,
                "title": "Treino de hoje",
                "description": "Siga a próxima aula recomendada da trilha.",
            }

    if lessons:
        return {
            "kind": "review",
            "lesson": lessons[-1],
            "progress": progress_map.get(lessons[-1].id),
            "title": "Revisão",
            "description": "Você concluiu a trilha publicada. Revise a última aula.",
        }

    return None


def grouped_lessons_for_user(user_id):
    lessons = get_published_lessons()
    progress_map = get_progress_map(user_id)
    groups = []
    group_index = {}
    for lesson in lessons:
        module = lesson.module or "Curso de Guitarra"
        if module not in group_index:
            group_index[module] = {"title": module, "lessons": []}
            groups.append(group_index[module])
        group_index[module]["lessons"].append({
            "lesson": lesson,
            "progress": progress_map.get(lesson.id),
        })
    return groups


def complete_progress_if_ready(progress, lesson):
    resource_ids = {r.id for r in lesson.resources.order_by(LessonResource.order.asc()).all()}
    completed_ids = progress.completed_ids()
    if resource_ids and not resource_ids.issubset(completed_ids):
        progress.status = "in_progress"
        progress.completed_at = None
        return False

    checklist_state = progress.checklist_state()
    required_items = []
    for resource in lesson.resources.order_by(LessonResource.order.asc()).all():
        required_items.extend(f"{resource.id}:{item}" for item in resource.checklist_lines())

    if any(not checklist_state.get(item) for item in required_items):
        progress.status = "in_progress"
        progress.completed_at = None
        return False

    progress.status = "completed"
    progress.completed_at = progress.completed_at or datetime.utcnow()
    return True

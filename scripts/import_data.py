import json
import os
import sys
from app import create_app
from app.extensions import db
from app.guitar_study.models import Lesson, LessonResource, StepMedia
from app.school_admin.routes import process_media_input

def normalize_lesson_text(value):
    if isinstance(value, list):
        return "\n".join(str(item).strip() for item in value if str(item).strip())
    if value is None:
        return None
    return str(value).strip() or None

def normalize_json_text(value):
    import json
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    if value is None:
        return None
    return str(value).strip() or None

def import_data():
    app = create_app()
    with app.app_context():
        # Caminho do arquivo JSON
        file_path = '/workspace/bases/aulas_guitarra_iniciante_com_imagens_base64.json'
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Limpa as aulas bases antigas para evitar duplicidades no banco ao rodar a semente
        db.session.query(Lesson).filter_by(school_id=None).delete()
        db.session.commit()
            
        for l_data in data:
            new_lesson = Lesson(
                title=l_data['title'],
                description=l_data.get('description', ''),
                module=l_data.get('module'),
                level=l_data.get('level'),
                estimated_minutes=l_data.get('estimated_minutes'),
                objectives=normalize_lesson_text(l_data.get('objectives')),
                prerequisites=normalize_lesson_text(l_data.get('prerequisites')),
                practice_focus=normalize_lesson_text(l_data.get('practice_focus')),
                order=l_data.get('order', 0),
                is_published=l_data.get('is_published', True),
                school_id=None # Aula base
            )
            db.session.add(new_lesson)
            db.session.flush()
            
            for s_data in l_data.get('steps', []):
                # Processa o path (que pode ser base64)
                raw_path = s_data.get('path')
                processed_path = process_media_input(raw_path, new_lesson.id, None, s_data.get('resource_type'))
                
                new_step = LessonResource(
                    lesson_id=new_lesson.id,
                    title=s_data['title'],
                    content=s_data.get('content', ''),
                    resource_type=s_data.get('resource_type', 'none'),
                    path=processed_path,
                    exercise_type=s_data.get('exercise_type') or None,
                    exercise_params=normalize_json_text(s_data.get('exercise_params')),
                    checklist_items=normalize_lesson_text(s_data.get('checklist_items')),
                    order=s_data.get('order', 0)
                )
                db.session.add(new_step)
        
        db.session.commit()
        print("Importação concluída com sucesso.")

if __name__ == '__main__':
    import_data()

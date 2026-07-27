import json
import os
import sys
from app import create_app
from app.extensions import db
from app.guitar_study.models import Lesson, LessonResource, StepMedia
from app.school_admin.routes import process_media_input

def import_data():
    app = create_app()
    with app.app_context():
        # Caminho do arquivo JSON
        file_path = '/workspace/bases/aulas_guitarra_iniciante_com_imagens_base64.json'
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for l_data in data:
            new_lesson = Lesson(
                title=l_data['title'],
                description=l_data.get('description', ''),
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
                    order=s_data.get('order', 0)
                )
                db.session.add(new_step)
        
        db.session.commit()
        print("Importação concluída com sucesso.")

if __name__ == '__main__':
    import_data()

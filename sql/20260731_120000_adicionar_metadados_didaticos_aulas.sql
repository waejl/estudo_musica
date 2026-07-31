ALTER TABLE lessons
    ADD COLUMN IF NOT EXISTS module VARCHAR(120),
    ADD COLUMN IF NOT EXISTS level VARCHAR(30),
    ADD COLUMN IF NOT EXISTS estimated_minutes INTEGER,
    ADD COLUMN IF NOT EXISTS objectives TEXT,
    ADD COLUMN IF NOT EXISTS prerequisites TEXT,
    ADD COLUMN IF NOT EXISTS practice_focus TEXT;

ALTER TABLE user_settings
    ADD COLUMN IF NOT EXISTS learning_mode VARCHAR(20) NOT NULL DEFAULT 'beginner';

ALTER TABLE lesson_resources
    ADD COLUMN IF NOT EXISTS exercise_type VARCHAR(80),
    ADD COLUMN IF NOT EXISTS exercise_params TEXT,
    ADD COLUMN IF NOT EXISTS checklist_items TEXT;

ALTER TABLE study_sessions
    ADD COLUMN IF NOT EXISTS lesson_id INTEGER REFERENCES lessons(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS resource_id INTEGER REFERENCES lesson_resources(id) ON DELETE SET NULL;

CREATE TABLE IF NOT EXISTS lesson_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    lesson_id INTEGER NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
    current_resource_id INTEGER REFERENCES lesson_resources(id) ON DELETE SET NULL,
    completed_resource_ids TEXT,
    checklist_data TEXT,
    status VARCHAR(30) NOT NULL DEFAULT 'in_progress',
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_lesson_progress_user_lesson UNIQUE (user_id, lesson_id)
);

CREATE INDEX IF NOT EXISTS idx_study_sessions_lesson_id ON study_sessions(lesson_id);
CREATE INDEX IF NOT EXISTS idx_study_sessions_resource_id ON study_sessions(resource_id);
CREATE INDEX IF NOT EXISTS idx_lesson_progress_user_id ON lesson_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_lesson_progress_lesson_id ON lesson_progress(lesson_id);

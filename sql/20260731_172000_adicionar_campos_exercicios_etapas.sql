-- Adicionar colunas de integração de exercícios e checklist na tabela lesson_resources no PostgreSQL
ALTER TABLE lesson_resources ADD COLUMN IF NOT EXISTS exercise_type VARCHAR(50) NULL;
ALTER TABLE lesson_resources ADD COLUMN IF NOT EXISTS exercise_params TEXT NULL;
ALTER TABLE lesson_resources ADD COLUMN IF NOT EXISTS checklist_items TEXT NULL;

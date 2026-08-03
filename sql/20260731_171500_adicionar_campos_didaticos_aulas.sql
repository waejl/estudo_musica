-- Adicionar colunas didáticas de elite na tabela lessons no PostgreSQL
ALTER TABLE lessons ADD COLUMN IF NOT EXISTS module VARCHAR(120) NULL;
ALTER TABLE lessons ADD COLUMN IF NOT EXISTS level VARCHAR(30) NULL;
ALTER TABLE lessons ADD COLUMN IF NOT EXISTS estimated_minutes INTEGER NULL;
ALTER TABLE lessons ADD COLUMN IF NOT EXISTS objectives TEXT NULL;
ALTER TABLE lessons ADD COLUMN IF NOT EXISTS prerequisites TEXT NULL;
ALTER TABLE lessons ADD COLUMN IF NOT EXISTS practice_focus TEXT NULL;

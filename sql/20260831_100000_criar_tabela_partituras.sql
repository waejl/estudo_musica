-- Script SQL de criação de tabela compatível com PostgreSQL
CREATE TABLE IF NOT EXISTS sheet_music (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    data TEXT NOT NULL, -- Armazena os dados da partitura em formato JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criação da função de trigger para PostgreSQL que atualiza o updated_at
CREATE OR REPLACE FUNCTION update_sheet_music_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Criação do trigger associado
DROP TRIGGER IF EXISTS trg_update_sheet_music_updated_at ON sheet_music;
CREATE TRIGGER trg_update_sheet_music_updated_at
BEFORE UPDATE ON sheet_music
FOR EACH ROW
EXECUTE FUNCTION update_sheet_music_updated_at_column();

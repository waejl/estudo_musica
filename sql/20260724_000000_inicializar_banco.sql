-- Criação do banco de dados (se necessário, o entrypoint já cria o POSTGRES_DB)
-- Mas criamos as tabelas necessárias para o Guitar Study.

-- Tabela de Usuários
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP
);

-- Tabela de Preferências de Usuário
CREATE TABLE IF NOT EXISTS user_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tuning_id VARCHAR(50) NOT NULL DEFAULT 'standard',
    fret_count INTEGER NOT NULL DEFAULT 22,
    accidentals_preference VARCHAR(10) NOT NULL DEFAULT 'sharps',
    theme VARCHAR(10) NOT NULL DEFAULT 'dark'
);

-- Tabela de Afinações Personalizadas
CREATE TABLE IF NOT EXISTS custom_tunings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    notes VARCHAR(100) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Favoritos
CREATE TABLE IF NOT EXISTS favorites (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category VARCHAR(50) NOT NULL,
    item_key VARCHAR(100) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Sessões de Estudo
CREATE TABLE IF NOT EXISTS study_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category VARCHAR(50) NOT NULL,
    item_key VARCHAR(100) NOT NULL,
    duration_minutes INTEGER NOT NULL,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Tentativas de Exercícios
CREATE TABLE IF NOT EXISTS exercise_attempts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    exercise_type VARCHAR(50) NOT NULL,
    questions_count INTEGER NOT NULL,
    correct_count INTEGER NOT NULL,
    incorrect_count INTEGER NOT NULL,
    score_percentage DOUBLE PRECISION NOT NULL,
    time_spent_seconds INTEGER NOT NULL,
    difficulty VARCHAR(20) NOT NULL DEFAULT 'medium',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Metas de Estudos
CREATE TABLE IF NOT EXISTS study_goals (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    target_minutes INTEGER NOT NULL,
    current_minutes INTEGER NOT NULL DEFAULT 0,
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    deadline DATE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Itens Recentes
CREATE TABLE IF NOT EXISTS recent_items (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category VARCHAR(50) NOT NULL,
    item_key VARCHAR(100) NOT NULL,
    last_accessed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_favorites_user_category ON favorites(user_id, category);
CREATE INDEX IF NOT EXISTS idx_study_sessions_user ON study_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_exercise_attempts_user ON exercise_attempts(user_id);
CREATE INDEX IF NOT EXISTS idx_recent_items_user ON recent_items(user_id);

-- Inserção de Usuário de Demonstração (Senha: admin123)
-- Hash gerado no Werkzeug com scrypt padrão
INSERT INTO users (id, name, username, email, password_hash, is_active, created_at, updated_at)
VALUES (
    1, 
    'Usuário de Demonstração', 
    'demo', 
    'demo@guitarstudy.com', 
    'scrypt:32768:8:1$uH3G7VvF$dca24fb08d0e741e40fb87b92648fbcf9ff45091c5211910606f366bca50125211b7dfb3d274bfcfec78d9101d2b7c62d04a696236b2829ec9bc8e56c547cb07', 
    TRUE, 
    CURRENT_TIMESTAMP, 
    CURRENT_TIMESTAMP
) ON CONFLICT (id) DO NOTHING;

-- Configuração inicial para o usuário de demonstração
INSERT INTO user_settings (id, user_id, tuning_id, fret_count, accidentals_preference, theme)
VALUES (
    1, 
    1, 
    'standard', 
    22, 
    'sharps', 
    'dark'
) ON CONFLICT (id) DO NOTHING;

-- Sementes de dados para sessões e exercícios para o dashboard iniciar preenchido
INSERT INTO study_sessions (user_id, category, item_key, duration_minutes, notes, created_at)
VALUES 
(1, 'scale', 'C_major', 15, 'Praticando o digito clássico de dó maior na primeira posição.', CURRENT_TIMESTAMP - INTERVAL '3 days'),
(1, 'fretboard', 'notes_identification', 10, 'Treino de identificação de notas naturais nas cordas E e A.', CURRENT_TIMESTAMP - INTERVAL '2 days'),
(1, 'mode', 'A_dorian', 20, 'Estudo do modo dórico de lá maior. Foco na nota característica (F#).', CURRENT_TIMESTAMP - INTERVAL '1 day'),
(1, 'chord', 'C_major_7', 10, 'Praticando pestanas com sétima maior na forma de Lá (CAGED).', CURRENT_TIMESTAMP)
ON CONFLICT DO NOTHING;

INSERT INTO exercise_attempts (user_id, exercise_type, questions_count, correct_count, incorrect_count, score_percentage, time_spent_seconds, difficulty, created_at)
VALUES 
(1, 'identify_note', 10, 8, 2, 80.0, 45, 'easy', CURRENT_TIMESTAMP - INTERVAL '3 days'),
(1, 'find_note', 10, 7, 3, 70.0, 60, 'medium', CURRENT_TIMESTAMP - INTERVAL '2 days'),
(1, 'intervals', 5, 5, 0, 100.0, 30, 'medium', CURRENT_TIMESTAMP - INTERVAL '1 day')
ON CONFLICT DO NOTHING;

INSERT INTO study_goals (user_id, title, target_minutes, current_minutes, is_completed, deadline, created_at)
VALUES 
(1, 'Dominar o Braço da Guitarra (Notas Naturais)', 120, 10, FALSE, CURRENT_DATE + INTERVAL '7 days', CURRENT_TIMESTAMP),
(1, 'Praticar Escala Pentatônica Diariamente', 60, 60, TRUE, CURRENT_DATE - INTERVAL '1 day', CURRENT_TIMESTAMP - INTERVAL '5 days')
ON CONFLICT DO NOTHING;

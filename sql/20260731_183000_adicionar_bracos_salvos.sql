CREATE TABLE IF NOT EXISTS saved_fretboard_maps (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    tuning_id VARCHAR(50),
    fret_count INTEGER,
    tonic VARCHAR(10),
    display_type VARCHAR(30) NOT NULL DEFAULT 'notes',
    notes_data TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_saved_fretboard_maps_user_id ON saved_fretboard_maps(user_id);

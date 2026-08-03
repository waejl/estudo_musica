-- sql/20260729_170000_adicionar_hand_orientation.sql
ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS hand_orientation VARCHAR(20) DEFAULT 'right_handed' NOT NULL;

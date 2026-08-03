-- sql/20260729_163000_seed_usuario_demo.sql

WITH inserted_user AS (
    INSERT INTO users (name, username, email, password_hash, role, is_active)
    VALUES (
        'Demonstração', 
        'demo', 
        'demo@estudomusica.com', 
        'scrypt:32768:8:1$YpwSSVtVYuQYSo2k$99a8e05a2abe9134b2afb2121b8ad2368f80be838d0c9945b85c157d8b0686ba40a759bd24e225f40558dfc4cb4c41b225e02e7f90117cffc9ca7cd1be5985ea', 
        'STUDENT', 
        TRUE
    )
    ON CONFLICT (username) DO UPDATE SET password_hash = EXCLUDED.password_hash
    RETURNING id
)
INSERT INTO user_settings (user_id)
SELECT id FROM inserted_user
ON CONFLICT DO NOTHING;

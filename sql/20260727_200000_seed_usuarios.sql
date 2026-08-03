-- sql/20260727_200000_seed_usuarios.sql

INSERT INTO users (name, username, email, password_hash, role) VALUES
('Super Admin', 'superadmin', 'super@admin.com', 'scrypt:32768:8:1$X8WvcqAdZZBRpgBO$cd50afd331a3ff9b0fa9813b963e5f77baf0c1d7052ec68c9c80084f6b802468bddb8794192e492fe4903d18a0b43ba34f3edb72bca32bbf20a2dcd82801428e', 'SUPER_ADMIN'),
('Admin da Escola', 'schooladmin', 'school@admin.com', 'scrypt:32768:8:1$X8WvcqAdZZBRpgBO$cd50afd331a3ff9b0fa9813b963e5f77baf0c1d7052ec68c9c80084f6b802468bddb8794192e492fe4903d18a0b43ba34f3edb72bca32bbf20a2dcd82801428e', 'SCHOOL_ADMIN'),
('Professor Exemplo', 'teacher', 'teacher@school.com', 'scrypt:32768:8:1$X8WvcqAdZZBRpgBO$cd50afd331a3ff9b0fa9813b963e5f77baf0c1d7052ec68c9c80084f6b802468bddb8794192e492fe4903d18a0b43ba34f3edb72bca32bbf20a2dcd82801428e', 'TEACHER'),
('Aluno Exemplo', 'student', 'student@school.com', 'scrypt:32768:8:1$X8WvcqAdZZBRpgBO$cd50afd331a3ff9b0fa9813b963e5f77baf0c1d7052ec68c9c80084f6b802468bddb8794192e492fe4903d18a0b43ba34f3edb72bca32bbf20a2dcd82801428e', 'STUDENT')
ON CONFLICT (username) DO UPDATE SET password_hash = EXCLUDED.password_hash, role = EXCLUDED.role;

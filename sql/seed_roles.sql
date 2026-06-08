-- ============================================================
-- seed_roles.sql
-- Cria os roles base do sistema de autenticação.
-- Executar ANTES de seed_usuarios_demo.sql
-- Seguro para re-executar: usa INSERT IGNORE
-- ============================================================

INSERT IGNORE INTO roles (id, nombre) VALUES
  (1, 'admin'),
  (2, 'docente'),
  (3, 'aluno');

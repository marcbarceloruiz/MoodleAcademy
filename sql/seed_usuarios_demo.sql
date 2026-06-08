-- ============================================================
-- seed_usuarios_demo.sql
-- Utilizadores de demonstração com passwords hashadas (werkzeug/scrypt).
-- Executar DEPOIS de seed_roles.sql
-- Seguro para re-executar: usa INSERT IGNORE
--
-- Credenciais:
--   admin    / admin123
--   docente  / docente123
--   aluno    / aluno123
-- ============================================================

INSERT IGNORE INTO usuarios
  (id, username, email, password_hash, nome, apelido, activo)
VALUES
  (
    1,
    'admin',
    'admin@academiaprofissional.pt',
    'scrypt:32768:8:1$96P3plZAbS7sfOR9$da6a907165893bc67fd5148ad4ba0f78bbee83096bab9e7da78f96eb4b9338736d94657de0b7b11ecea13a1e5000daf14eede153b57fe31dfa71d7cf661ec36c',
    'Administrador',
    'Sistema',
    1
  ),
  (
    2,
    'docente',
    'docente@academiaprofissional.pt',
    'scrypt:32768:8:1$n02EEyEkf9egrSA0$b1a553a7eb521c5eacb2ed26505a62d9c351177c21e048ca3b2a23976cfb07ae8e9e0f6a93530fc8edf4669d58ff1e996c82ed59f8c07ca9763af8b7650a7b2d',
    'Formador',
    'Demo',
    1
  ),
  (
    3,
    'aluno',
    'aluno@academiaprofissional.pt',
    'scrypt:32768:8:1$Bt4SMXaZOJJEOwfu$728a3b5a68e922e2c17ccd7ed55790cdd8ffb1ca1d1bd8e1dddf77889f2a6bc7abd55ecfe8c60149452bd0b58d60a61c1e2811af1ca20fd74bb068cbacc7232b',
    'Aluno',
    'Demo',
    1
  );

-- Atribuir roles
INSERT IGNORE INTO usuario_roles (usuario_id, rol_id) VALUES
  (1, 1),  -- admin → admin
  (2, 2),  -- docente → docente
  (3, 3);  -- aluno → aluno

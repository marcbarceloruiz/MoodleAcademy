-- ============================================================
-- seed_auth_final.sql
-- Seed completo e seguro para o sistema de autenticação.
--
-- SEGURANÇA:
--   • Sem DROP, TRUNCATE ou DELETE
--   • Usa CREATE TABLE IF NOT EXISTS
--   • Usa INSERT IGNORE para roles e usuario_roles
--   • Usa INSERT ... SELECT ... WHERE NOT EXISTS para usuarios
--   • Re-executável sem duplicar dados
--
-- Executar em phpMyAdmin na base de dados do campus.
-- Substitui/consolida: seed_estrutura_extra + seed_roles + seed_usuarios_demo
-- ============================================================


-- ── 1. TABELAS ──────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS roles (
    id     INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50)  NOT NULL,
    UNIQUE KEY uq_roles_nombre (nombre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS usuarios (
    id            INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(80)  NOT NULL,
    email         VARCHAR(120) NULL,
    password_hash VARCHAR(255) NOT NULL,
    nome          VARCHAR(120) NULL,
    apelido       VARCHAR(120) NULL,
    activo        TINYINT(1)   NOT NULL DEFAULT 1,
    criado_em     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_usuarios_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS usuario_roles (
    usuario_id INT UNSIGNED NOT NULL,
    rol_id     INT UNSIGNED NOT NULL,
    PRIMARY KEY (usuario_id, rol_id),
    CONSTRAINT fk_ur_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE,
    CONSTRAINT fk_ur_rol     FOREIGN KEY (rol_id)     REFERENCES roles    (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── 2. ROLES BASE ────────────────────────────────────────────

INSERT IGNORE INTO roles (id, nombre) VALUES
    (1, 'admin'),
    (2, 'docente'),
    (3, 'aluno');


-- ── 3. UTILIZADORES DEMO ─────────────────────────────────────
--
-- Palavras-passe geradas com werkzeug.security.generate_password_hash (scrypt).
--
--   admin   → admin123
--   docente → docente123
--   aluno   → aluno123
--
-- ATENÇÃO: Alterar em produção antes de publicar.
-- Nomes genéricos — sem nomes pessoais inventados.

INSERT INTO usuarios (username, email, password_hash, nome, apelido, activo)
SELECT
    'admin',
    'admin@academiaprofissional.pt',
    'scrypt:32768:8:1$WPXP0B4Xs3lmvvvk$e0bed6c094a8795290535ee9b10415ea3161e6307bd766d9e8c6059d3530f0c2f42823429968484baefeaf5e26b13c0c8a95dbb058ac606c9bfa89792d1b17f0',
    'Administrador', '', 1
WHERE NOT EXISTS (SELECT 1 FROM usuarios WHERE username = 'admin');

INSERT INTO usuarios (username, email, password_hash, nome, apelido, activo)
SELECT
    'docente',
    'docente@academiaprofissional.pt',
    'scrypt:32768:8:1$Q7pik1T7bPmvd8G9$330838ecbf4ec6a73dc1e199bd067b25f7e7fa8fbb59671ac4abe8287c2a7d43d9899f8b4b3c4792d61b8b1c80dd1c58344cd91766824487304ccf013914a129',
    'Docente', '', 1
WHERE NOT EXISTS (SELECT 1 FROM usuarios WHERE username = 'docente');

INSERT INTO usuarios (username, email, password_hash, nome, apelido, activo)
SELECT
    'aluno',
    'aluno@academiaprofissional.pt',
    'scrypt:32768:8:1$FYkDJljPbEeY3rlo$d78c0dfc232ece44762c2a680cc7d6073eb9cc60cb2eca168dace6985ec89476e1a8959e98f62942996b1ee0d25382c68de462084943a80aadfd2a4d93d1bbda',
    'Aluno', '', 1
WHERE NOT EXISTS (SELECT 1 FROM usuarios WHERE username = 'aluno');


-- ── 4. ATRIBUIÇÃO DE ROLES ───────────────────────────────────

INSERT IGNORE INTO usuario_roles (usuario_id, rol_id)
SELECT u.id, r.id
FROM usuarios u, roles r
WHERE u.username = 'admin' AND r.nombre = 'admin';

INSERT IGNORE INTO usuario_roles (usuario_id, rol_id)
SELECT u.id, r.id
FROM usuarios u, roles r
WHERE u.username = 'docente' AND r.nombre = 'docente';

INSERT IGNORE INTO usuario_roles (usuario_id, rol_id)
SELECT u.id, r.id
FROM usuarios u, roles r
WHERE u.username = 'aluno' AND r.nombre = 'aluno';


-- ── VERIFICAÇÃO FINAL (apenas leitura, não modifica nada) ────
-- SELECT u.username, u.nome, r.nombre AS rol
-- FROM usuarios u
-- JOIN usuario_roles ur ON ur.usuario_id = u.id
-- JOIN roles r ON r.id = ur.rol_id
-- ORDER BY u.id;

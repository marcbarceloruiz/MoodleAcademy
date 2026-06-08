-- ============================================================
-- seed_estrutura_extra.sql
-- Cria as tabelas de autenticação SE NÃO EXISTIREM.
-- Executar PRIMEIRO, antes de seed_roles.sql e seed_usuarios_demo.sql
-- Seguro para re-executar: usa CREATE TABLE IF NOT EXISTS
-- ============================================================

-- Tabela de utilizadores
CREATE TABLE IF NOT EXISTS usuarios (
    id            INT          NOT NULL AUTO_INCREMENT,
    username      VARCHAR(80)  NOT NULL UNIQUE,
    email         VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(512) NOT NULL,
    nome          VARCHAR(100) DEFAULT NULL,
    apelido       VARCHAR(100) DEFAULT NULL,
    activo        TINYINT(1)   NOT NULL DEFAULT 1,
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela de roles
CREATE TABLE IF NOT EXISTS roles (
    id     INT         NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela de associação utilizador ↔ role (N:M)
CREATE TABLE IF NOT EXISTS usuario_roles (
    usuario_id INT NOT NULL,
    rol_id     INT NOT NULL,
    PRIMARY KEY (usuario_id, rol_id),
    CONSTRAINT fk_ur_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE,
    CONSTRAINT fk_ur_rol     FOREIGN KEY (rol_id)     REFERENCES roles    (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

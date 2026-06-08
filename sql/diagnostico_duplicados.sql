-- ============================================================
-- diagnostico_duplicados.sql
-- Consultas de diagnóstico para detetar duplicados e inconsistências.
-- Executar em phpMyAdmin para verificar o estado da BD.
-- NÃO faz alterações — apenas SELECT.
-- ============================================================

-- 1. Utilizadores com o mesmo username
SELECT username, COUNT(*) AS total
FROM usuarios
GROUP BY username
HAVING COUNT(*) > 1;

-- 2. Utilizadores com o mesmo email
SELECT email, COUNT(*) AS total
FROM usuarios
GROUP BY email
HAVING COUNT(*) > 1;

-- 3. Roles duplicados
SELECT nombre, COUNT(*) AS total
FROM roles
GROUP BY nombre
HAVING COUNT(*) > 1;

-- 4. Atribuições de role duplicadas
SELECT usuario_id, rol_id, COUNT(*) AS total
FROM usuario_roles
GROUP BY usuario_id, rol_id
HAVING COUNT(*) > 1;

-- 5. Utilizadores sem role atribuído
SELECT u.id, u.username, u.email
FROM usuarios u
LEFT JOIN usuario_roles ur ON ur.usuario_id = u.id
WHERE ur.rol_id IS NULL;

-- 6. Utilizadores demo criados
SELECT u.id, u.username, u.nome, u.activo, r.nombre AS role
FROM usuarios u
LEFT JOIN usuario_roles ur ON ur.usuario_id = u.id
LEFT JOIN roles r ON r.id = ur.rol_id
ORDER BY u.id;

-- 7. Áreas institucionais sem slug
SELECT id, titulo, slug
FROM areas_institucionais
WHERE slug IS NULL OR slug = '';

-- 8. Documentos sem área associada
SELECT d.id, d.titulo
FROM documentos_institucionais d
LEFT JOIN areas_institucionais a ON a.id = d.area_id
WHERE a.id IS NULL;

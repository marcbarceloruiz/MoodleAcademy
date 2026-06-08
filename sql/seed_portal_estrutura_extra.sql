-- ============================================================
-- seed_portal_estrutura_extra.sql
-- Insere de forma segura as novas áreas institucionais
-- (CTEs, EFA, Formação Modular) e os seus documentos base.
--
-- SEGURANÇA:
--   • Sem DROP, TRUNCATE ou DELETE
--   • Usa INSERT ... SELECT ... WHERE NOT EXISTS
--   • Pode ser re-executado sem duplicar dados
--
-- Executar APÓS o seed inicial da estrutura principal.
-- ============================================================


-- ── ÁREAS INSTITUCIONAIS ──────────────────────────────────

INSERT INTO areas_institucionais (slug, titulo, descricao, conteudo, ativo)
SELECT 'centros-tecnologicos',
       'Centros Tecnológicos',
       'Centros de referência tecnológica: CTE Informática e CTE Industrial.',
       'Os Centros Tecnológicos são espaços de excelência para formação avançada em tecnologia, indústria e inovação.',
       1
WHERE NOT EXISTS (
    SELECT 1 FROM areas_institucionais WHERE slug = 'centros-tecnologicos'
);

INSERT INTO areas_institucionais (slug, titulo, descricao, conteudo, ativo)
SELECT 'cte-informatica',
       'CTE Informática',
       'Programação, Inteligência Artificial, Robótica e Realidade Virtual.',
       'O CTE de Informática oferece recursos avançados em programação, IA, robótica e realidade virtual para alunos e formadores.',
       1
WHERE NOT EXISTS (
    SELECT 1 FROM areas_institucionais WHERE slug = 'cte-informatica'
);

INSERT INTO areas_institucionais (slug, titulo, descricao, conteudo, ativo)
SELECT 'cte-industrial',
       'CTE Industrial',
       'CNC, CAD/CAM, Automatização Industrial e Indústria 5.0.',
       'O CTE Industrial disponibiliza equipamentos de última geração em maquinação CNC, CAD/CAM e automação para formação técnica.',
       1
WHERE NOT EXISTS (
    SELECT 1 FROM areas_institucionais WHERE slug = 'cte-industrial'
);

INSERT INTO areas_institucionais (slug, titulo, descricao, conteudo, ativo)
SELECT 'efa',
       'EFA — Educação e Formação de Adultos',
       'Percursos EFA Escolar e Profissional para adultos.',
       'Os percursos EFA destinam-se a adultos que pretendem obter uma qualificação escolar e/ou profissional.',
       1
WHERE NOT EXISTS (
    SELECT 1 FROM areas_institucionais WHERE slug = 'efa'
);

INSERT INTO areas_institucionais (slug, titulo, descricao, conteudo, ativo)
SELECT 'efa-escolar',
       'EFA Escolar',
       'Componente escolar dos percursos EFA.',
       'A componente escolar dos percursos EFA abrange as áreas de Português, Matemática e Cidadania.',
       1
WHERE NOT EXISTS (
    SELECT 1 FROM areas_institucionais WHERE slug = 'efa-escolar'
);

INSERT INTO areas_institucionais (slug, titulo, descricao, conteudo, ativo)
SELECT 'efa-profissional',
       'EFA Profissional',
       'Componente profissional dos percursos EFA.',
       'A componente profissional dos percursos EFA inclui formação técnica, FCT e projeto integrado.',
       1
WHERE NOT EXISTS (
    SELECT 1 FROM areas_institucionais WHERE slug = 'efa-profissional'
);

INSERT INTO areas_institucionais (slug, titulo, descricao, conteudo, ativo)
SELECT 'formacao-modular-certificada',
       'Formação Modular Certificada',
       'Cursos modulares certificados para desenvolvimento de competências.',
       'A Formação Modular Certificada permite adquirir competências por módulos, acumulando créditos para certificação.',
       1
WHERE NOT EXISTS (
    SELECT 1 FROM areas_institucionais WHERE slug = 'formacao-modular-certificada'
);


-- ── DOCUMENTOS BASE ───────────────────────────────────────
-- Inserção segura usando sub-SELECT para obter area_id pelo slug.

-- centros-tecnologicos
INSERT INTO documentos_institucionais (area_id, titulo, tipo, descricao, url, orden, visible)
SELECT a.id, 'Apresentação dos CTEs', 'Documento',
       'Visão geral dos Centros Tecnológicos da escola.', NULL, 1, 1
FROM areas_institucionais a
WHERE a.slug = 'centros-tecnologicos'
  AND NOT EXISTS (
      SELECT 1 FROM documentos_institucionais d
      WHERE d.area_id = a.id AND d.titulo = 'Apresentação dos CTEs'
  );

INSERT INTO documentos_institucionais (area_id, titulo, tipo, descricao, url, orden, visible)
SELECT a.id, 'Oferta Formativa dos CTEs', 'PDF',
       'Áreas de formação e competências disponíveis.', NULL, 2, 1
FROM areas_institucionais a
WHERE a.slug = 'centros-tecnologicos'
  AND NOT EXISTS (
      SELECT 1 FROM documentos_institucionais d
      WHERE d.area_id = a.id AND d.titulo = 'Oferta Formativa dos CTEs'
  );

-- cte-informatica
INSERT INTO documentos_institucionais (area_id, titulo, tipo, descricao, url, orden, visible)
SELECT a.id, 'Guia de Competências CTE Informática', 'PDF',
       'Programação, IA, Robótica e Realidade Virtual.', NULL, 1, 1
FROM areas_institucionais a
WHERE a.slug = 'cte-informatica'
  AND NOT EXISTS (
      SELECT 1 FROM documentos_institucionais d
      WHERE d.area_id = a.id AND d.titulo = 'Guia de Competências CTE Informática'
  );

INSERT INTO documentos_institucionais (area_id, titulo, tipo, descricao, url, orden, visible)
SELECT a.id, 'Percursos de Programação', 'PDF',
       'Python, Java, JavaScript e projetos reais.', NULL, 2, 1
FROM areas_institucionais a
WHERE a.slug = 'cte-informatica'
  AND NOT EXISTS (
      SELECT 1 FROM documentos_institucionais d
      WHERE d.area_id = a.id AND d.titulo = 'Percursos de Programação'
  );

-- cte-industrial
INSERT INTO documentos_institucionais (area_id, titulo, tipo, descricao, url, orden, visible)
SELECT a.id, 'Guia de Máquinas CNC', 'PDF',
       'Inventário e especificações técnicas.', NULL, 1, 1
FROM areas_institucionais a
WHERE a.slug = 'cte-industrial'
  AND NOT EXISTS (
      SELECT 1 FROM documentos_institucionais d
      WHERE d.area_id = a.id AND d.titulo = 'Guia de Máquinas CNC'
  );

INSERT INTO documentos_institucionais (area_id, titulo, tipo, descricao, url, orden, visible)
SELECT a.id, 'Segurança Industrial', 'PDF',
       'Normas, EPI e procedimentos de segurança.', NULL, 2, 1
FROM areas_institucionais a
WHERE a.slug = 'cte-industrial'
  AND NOT EXISTS (
      SELECT 1 FROM documentos_institucionais d
      WHERE d.area_id = a.id AND d.titulo = 'Segurança Industrial'
  );

-- efa
INSERT INTO documentos_institucionais (area_id, titulo, tipo, descricao, url, orden, visible)
SELECT a.id, 'O que é EFA?', 'Documento',
       'Explicação geral dos percursos EFA.', NULL, 1, 1
FROM areas_institucionais a
WHERE a.slug = 'efa'
  AND NOT EXISTS (
      SELECT 1 FROM documentos_institucionais d
      WHERE d.area_id = a.id AND d.titulo = 'O que é EFA?'
  );

INSERT INTO documentos_institucionais (area_id, titulo, tipo, descricao, url, orden, visible)
SELECT a.id, 'Processo de Inscrição', 'Formulário',
       'Como candidatar-se a um percurso EFA.', NULL, 2, 1
FROM areas_institucionais a
WHERE a.slug = 'efa'
  AND NOT EXISTS (
      SELECT 1 FROM documentos_institucionais d
      WHERE d.area_id = a.id AND d.titulo = 'Processo de Inscrição'
  );

-- efa-escolar
INSERT INTO documentos_institucionais (area_id, titulo, tipo, descricao, url, orden, visible)
SELECT a.id, 'Guia da Componente Escolar', 'PDF',
       'Estrutura, avaliação e disciplinas.', NULL, 1, 1
FROM areas_institucionais a
WHERE a.slug = 'efa-escolar'
  AND NOT EXISTS (
      SELECT 1 FROM documentos_institucionais d
      WHERE d.area_id = a.id AND d.titulo = 'Guia da Componente Escolar'
  );

-- efa-profissional
INSERT INTO documentos_institucionais (area_id, titulo, tipo, descricao, url, orden, visible)
SELECT a.id, 'Guia da Componente Profissional', 'PDF',
       'Estrutura, FCT e avaliação profissional.', NULL, 1, 1
FROM areas_institucionais a
WHERE a.slug = 'efa-profissional'
  AND NOT EXISTS (
      SELECT 1 FROM documentos_institucionais d
      WHERE d.area_id = a.id AND d.titulo = 'Guia da Componente Profissional'
  );

INSERT INTO documentos_institucionais (area_id, titulo, tipo, descricao, url, orden, visible)
SELECT a.id, 'Formação em Contexto de Trabalho', 'Documento',
       'FCT: procedimentos, empresas e relatório final.', NULL, 2, 1
FROM areas_institucionais a
WHERE a.slug = 'efa-profissional'
  AND NOT EXISTS (
      SELECT 1 FROM documentos_institucionais d
      WHERE d.area_id = a.id AND d.titulo = 'Formação em Contexto de Trabalho'
  );

-- formacao-modular-certificada
INSERT INTO documentos_institucionais (area_id, titulo, tipo, descricao, url, orden, visible)
SELECT a.id, 'O que é FMC?', 'Documento',
       'Modelo modular e certificação por créditos.', NULL, 1, 1
FROM areas_institucionais a
WHERE a.slug = 'formacao-modular-certificada'
  AND NOT EXISTS (
      SELECT 1 FROM documentos_institucionais d
      WHERE d.area_id = a.id AND d.titulo = 'O que é FMC?'
  );

INSERT INTO documentos_institucionais (area_id, titulo, tipo, descricao, url, orden, visible)
SELECT a.id, 'Catálogo de Módulos', 'PDF',
       'Módulos disponíveis por área de formação.', NULL, 2, 1
FROM areas_institucionais a
WHERE a.slug = 'formacao-modular-certificada'
  AND NOT EXISTS (
      SELECT 1 FROM documentos_institucionais d
      WHERE d.area_id = a.id AND d.titulo = 'Catálogo de Módulos'
  );

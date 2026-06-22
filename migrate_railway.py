# -*- coding: utf-8 -*-
"""
Aplica todos os dados em falta na base de dados de produção (Railway).
Uso:
    DATABASE_URL="mysql+pymysql://user:pass@host:port/db" python migrate_railway.py
"""
import sys, os

# Aceitar DATABASE_URL por argumento ou variável de ambiente
if len(sys.argv) > 1:
    os.environ["DATABASE_URL"] = sys.argv[1]

if not os.environ.get("DATABASE_URL"):
    print("ERRO: Define DATABASE_URL como variável de ambiente ou argumento.")
    print('  Exemplo: python migrate_railway.py "mysql+pymysql://user:pass@host:port/db"')
    sys.exit(1)

sys.path.insert(0, os.path.dirname(__file__))
from app import create_app
from extensions import db
from sqlalchemy import text

app = create_app()

DEMO_URL = "/static/uploads/demo/documento-demo.pdf"

SECCOES = [
    ("Informação Geral",  "informacao-geral",  "Apresentação, objetivos e informação geral da disciplina."),
    ("Conteúdos",         "conteudos",         "Materiais de estudo, documentos e vídeos da disciplina."),
    ("Avaliação",         "avaliacao",         "Critérios de avaliação, testes e instrumentos de avaliação."),
    ("Evidências",        "evidencias",        "Trabalhos, projetos e evidências de aprendizagem."),
    ("Comunicação",       "comunicacao",       "Fórum de dúvidas e comunicação com o docente."),
]

RECURSOS_POR_SECAO = {
    "informacao-geral": [
        ("documento", "Programa da Disciplina"),
        ("documento", "Planificação Anual"),
        ("lectura",   "Apresentação da Disciplina"),
    ],
    "conteudos": [
        ("documento", "Ficha de Trabalho 1"),
        ("documento", "Ficha de Trabalho 2"),
        ("documento", "Ficha de Trabalho 3"),
        ("video",     "Vídeo Explicativo — Tema 1"),
        ("video",     "Vídeo Explicativo — Tema 2"),
        ("lectura",   "Resumo Teórico"),
    ],
    "avaliacao": [
        ("documento",    "Critérios de Avaliação"),
        ("cuestionario", "Teste de Avaliação"),
        ("tarea",        "Trabalho Prático"),
    ],
    "evidencias": [
        ("evidencia", "Portfólio de Evidências"),
        ("tarea",     "Projeto Final"),
    ],
    "comunicacao": [
        ("foro", "Fórum de Dúvidas"),
        ("foro", "Fórum de Discussão"),
    ],
}


def seed_disciplinas_for_ciclo(ciclo_id, disciplinas_by_ano):
    """Recria disciplinas/secciones/recursos para um ciclo."""
    anos = db.session.execute(text(
        "SELECT id, numero FROM anos_ciclo WHERE ciclo_id=:cid ORDER BY orden"
    ), {"cid": ciclo_id}).mappings().all()

    ano_ids = {a["numero"]: a["id"] for a in anos}
    if not ano_ids:
        print(f"  AVISO: Ciclo {ciclo_id} sem anos — a saltar.")
        return 0, 0, 0

    # Limpar disciplinas antigas
    for ano_id in ano_ids.values():
        old_discs = db.session.execute(text(
            "SELECT id FROM disciplinas_ciclo WHERE ano_id=:aid"
        ), {"aid": ano_id}).fetchall()
        for (disc_id,) in old_discs:
            old_secc = db.session.execute(text(
                "SELECT id FROM secciones_disciplina WHERE disciplina_id=:did"
            ), {"did": disc_id}).fetchall()
            for (secc_id,) in old_secc:
                db.session.execute(text("DELETE FROM recursos_disciplina WHERE seccion_id=:sid"), {"sid": secc_id})
            db.session.execute(text("DELETE FROM secciones_disciplina WHERE disciplina_id=:did"), {"did": disc_id})
        db.session.execute(text("DELETE FROM disciplinas_ciclo WHERE ano_id=:aid"), {"aid": ano_id})

    total_d = total_s = total_r = 0
    for numero, disciplinas in disciplinas_by_ano.items():
        if numero not in ano_ids:
            continue
        ano_id = ano_ids[numero]
        for ordem_d, (nome, tipo, horas) in enumerate(disciplinas, 1):
            r = db.session.execute(text("""
                INSERT INTO disciplinas_ciclo (ano_id, nombre, tipo, horas, orden)
                VALUES (:aid, :nom, :tipo, :h, :ord)
            """), {"aid": ano_id, "nom": nome, "tipo": tipo, "h": horas, "ord": ordem_d})
            disc_id = r.lastrowid
            total_d += 1

            for ordem_s, (titulo_s, slug_s, desc_s) in enumerate(SECCOES, 1):
                r2 = db.session.execute(text("""
                    INSERT INTO secciones_disciplina
                        (disciplina_id, titulo, slug, descripcion, visible, orden)
                    VALUES (:did, :titulo, :slug, :desc, 1, :ord)
                """), {"did": disc_id, "titulo": titulo_s, "slug": slug_s, "desc": desc_s, "ord": ordem_s})
                secc_id = r2.lastrowid
                total_s += 1

                for ordem_r, (tipo_r, titulo_r) in enumerate(RECURSOS_POR_SECAO[slug_s], 1):
                    url = DEMO_URL if tipo_r in ("documento", "video", "lectura", "evidencia") else None
                    db.session.execute(text("""
                        INSERT INTO recursos_disciplina
                            (seccion_id, tipo, titulo, url, visible, orden)
                        VALUES (:sid, :tipo, :titulo, :url, 1, :ord)
                    """), {"sid": secc_id, "tipo": tipo_r, "titulo": titulo_r, "url": url, "ord": ordem_r})
                    total_r += 1

    return total_d, total_s, total_r


with app.app_context():
    print(f"Conectado a: {str(db.engine.url).replace(':' + str(db.engine.url.password) + '@', ':***@')}")

    # ── 1. Tabelas novas ─────────────────────────────────────
    print("\n[1] Criar tabelas novas...")
    new_tables = [
        """CREATE TABLE IF NOT EXISTS recurso_conclusao (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id INT NOT NULL, recurso_id INT NOT NULL,
            completado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY uq_rc (usuario_id, recurso_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
        """CREATE TABLE IF NOT EXISTS forum_threads (
            id INT AUTO_INCREMENT PRIMARY KEY,
            recurso_id INT NOT NULL, titulo VARCHAR(255) NOT NULL,
            usuario_id INT NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            KEY idx_ft_recurso (recurso_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
        """CREATE TABLE IF NOT EXISTS forum_posts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            thread_id INT NOT NULL, usuario_id INT NOT NULL,
            conteudo TEXT NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            KEY idx_fp_thread (thread_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
        """CREATE TABLE IF NOT EXISTS questionarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            recurso_id INT NOT NULL UNIQUE, titulo VARCHAR(255) NOT NULL,
            descricao TEXT, created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
        """CREATE TABLE IF NOT EXISTS perguntas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            questionario_id INT NOT NULL, enunciado TEXT NOT NULL,
            tipo VARCHAR(50) NOT NULL DEFAULT 'multipla_escolha', ordem INT NOT NULL DEFAULT 0,
            KEY idx_pg_quiz (questionario_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
        """CREATE TABLE IF NOT EXISTS opcoes_resposta (
            id INT AUTO_INCREMENT PRIMARY KEY,
            pergunta_id INT NOT NULL, texto VARCHAR(500) NOT NULL,
            correta TINYINT(1) NOT NULL DEFAULT 0,
            KEY idx_or_pergunta (pergunta_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
        """CREATE TABLE IF NOT EXISTS tentativas_quiz (
            id INT AUTO_INCREMENT PRIMARY KEY,
            questionario_id INT NOT NULL, usuario_id INT NOT NULL,
            nota DECIMAL(5,2), iniciada_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            terminada_em DATETIME, KEY idx_tq_usuario (usuario_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
        """CREATE TABLE IF NOT EXISTS respostas_aluno (
            id INT AUTO_INCREMENT PRIMARY KEY,
            tentativa_id INT NOT NULL, pergunta_id INT NOT NULL,
            opcao_id INT, resposta_texto TEXT,
            KEY idx_ra_tentativa (tentativa_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
    ]
    for stmt in new_tables:
        try:
            db.session.execute(text(stmt))
            db.session.commit()
        except Exception as e:
            print(f"  AVISO: {e}")

    # ADD COLUMN IF NOT EXISTS (MySQL 8+ só)
    try:
        db.session.execute(text("ALTER TABLE entregas ADD COLUMN IF NOT EXISTS recurso_id INT DEFAULT NULL"))
        db.session.commit()
        print("  OK  entregas.recurso_id")
    except Exception:
        print("  OK  entregas.recurso_id (já existe ou não suportado)")

    # ── 2. Ciclo 8 — Sistemas de Computação e Redes ──────────
    print("\n[2] Ciclo 8 — Sistemas de Computação e Redes...")
    db.session.execute(text("""
        UPDATE ciclos_formativos SET
            nombre = 'Sistemas de Computação e Redes',
            nivel = 'Nível 4', duracion = '3 anos / 3175h',
            descripcion = 'O Curso Técnico/a de Sistemas de Computação e Redes forma profissionais qualificados para instalar, configurar, manter e administrar sistemas informáticos e redes de comunicação.'
        WHERE id = 8
    """))
    db.session.commit()

    SCR = {
        1: [
            ("Português", "sociocultural", 110), ("Inglês", "sociocultural", 110),
            ("Área de Integração", "sociocultural", 90),
            ("Tecnologias da Informação e Comunicação", "sociocultural", 100),
            ("Educação Física", "sociocultural", 70), ("Cidadania e Desenvolvimento", "sociocultural", 35),
            ("Matemática", "cientifica", 165), ("Físico-Química", "cientifica", 165),
            ("Arquitetura de Sistemas Computacionais", "tecnologica", 270),
            ("Educação Moral e Religiosa", "opcional", 27),
        ],
        2: [
            ("Português", "sociocultural", 110), ("Inglês Técnico", "sociocultural", 110),
            ("Área de Integração", "sociocultural", 90), ("Educação Física", "sociocultural", 70),
            ("Cidadania e Desenvolvimento", "sociocultural", 35),
            ("Matemática", "cientifica", 165), ("Físico-Química", "cientifica", 35),
            ("Redes de Comunicação e Administração", "tecnologica", 270),
            ("Programação e Desenvolvimento", "tecnologica", 205),
            ("Educação Moral e Religiosa", "opcional", 27),
        ],
        3: [
            ("Português", "sociocultural", 110), ("Inglês Técnico", "sociocultural", 75),
            ("Área de Integração", "sociocultural", 75), ("Educação Física", "sociocultural", 70),
            ("Segurança Informática e Administração de Sistemas", "tecnologica", 330),
            ("FCT — Formação em Contexto de Trabalho", "fct", 600),
            ("PAP — Prova de Aptidão Profissional", "pap", 0),
            ("Educação Moral e Religiosa", "opcional", 27),
        ],
    }
    d, s, r = seed_disciplinas_for_ciclo(8, SCR)
    print(f"  {d} disciplinas, {s} secciones, {r} recursos")
    db.session.commit()

    # ── 3. Ciclo 15 — EFA-DMM ────────────────────────────────
    print("\n[3] Ciclo 15 — EFA Desenho de Mobiliário e Construções em Madeira...")
    db.session.execute(text("""
        UPDATE ciclos_formativos SET
            nombre = 'Desenho de Mobiliário e Construções em Madeira',
            nivel = 'Nível 3', duracion = '1 a 2 anos',
            descripcion = 'Formação em design de mobiliário e trabalho em madeira, incluindo software CAD, maquinaria de marcenaria e acabamentos. Desenvolve competências de projeto, produção e controlo de qualidade.'
        WHERE id = 15
    """))
    db.session.commit()

    # Garantir que tem anos
    n_anos = db.session.execute(text("SELECT COUNT(*) FROM anos_ciclo WHERE ciclo_id=15")).scalar()
    if n_anos == 0:
        db.session.execute(text("""
            INSERT INTO anos_ciclo (ciclo_id, numero, ano_escolar, descripcion, orden) VALUES
            (15, 1, 'Percurso 1', 'Formação técnica base — Desenho e CAD.', 1),
            (15, 2, 'Percurso 2', 'Formação avançada — Madeira, CNC e FCT.', 2)
        """))
        db.session.commit()
        print("  Anos criados.")

    EFA_DMM = {
        1: [
            ("Desenho Técnico e Representação", "tecnologica", 150),
            ("CAD 2D", "tecnologica", 100),
            ("Modelação 3D", "tecnologica", 100),
            ("Materiais e Tecnologias da Madeira", "tecnologica", 75),
        ],
        2: [
            ("Estruturas e Construção em Madeira", "tecnologica", 150),
            ("Produção e Tecnologia CNC", "tecnologica", 100),
            ("Desenvolvimento de Produto", "tecnologica", 100),
            ("FCT — Formação Prática em Contexto de Trabalho", "fct", 210),
        ],
    }
    d, s, r = seed_disciplinas_for_ciclo(15, EFA_DMM)
    print(f"  {d} disciplinas, {s} secciones, {r} recursos")
    db.session.commit()

    print("\nMigração concluída com sucesso.")

"""
Blueprint: Funcionalidades do aluno.
Rutas: /cursos/recurso/<id>/concluir
       /cursos/recurso/<id>/entregar
       /as-minhas-entregas
       /forum/<recurso_id>
       /quiz/<recurso_id>
"""

import os
import uuid

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    current_app,
    flash,
    abort,
)
from sqlalchemy import text
from werkzeug.utils import secure_filename

from extensions import db
from decorators import login_required
from services.data_service import get_current_user

student_bp = Blueprint("student", __name__)


# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────

def _fetch_one(sql, params=None):
    try:
        return db.session.execute(text(sql), params or {}).mappings().first()
    except Exception as e:
        current_app.logger.error("[student] _fetch_one: %s", e, exc_info=True)
        return None


def _fetch_all(sql, params=None):
    try:
        return db.session.execute(text(sql), params or {}).mappings().all()
    except Exception as e:
        current_app.logger.error("[student] _fetch_all: %s", e, exc_info=True)
        return []


def _allowed_upload(filename):
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    allowed = current_app.config.get(
        "ALLOWED_UPLOAD_EXTENSIONS",
        {"pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt",
         "png", "jpg", "jpeg", "webp", "zip", "rar"},
    )
    return ext in allowed


def _current_usuario_id():
    return session.get("usuario_id")


def _ensure_tables():
    """Cria as tabelas novas se não existirem (idempotente)."""
    try:
        db.session.execute(text("SELECT 1"))
    except Exception:
        db.session.rollback()
        current_app.logger.warning("[student] _ensure_tables: DB não disponível, a saltar")
        return

    stmts = [
        """
        CREATE TABLE IF NOT EXISTS recurso_conclusao (
            id            INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id    INT NOT NULL,
            recurso_id    INT NOT NULL,
            completado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY uq_rc (usuario_id, recurso_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,
        """
        CREATE TABLE IF NOT EXISTS forum_threads (
            id         INT AUTO_INCREMENT PRIMARY KEY,
            recurso_id INT NOT NULL,
            titulo     VARCHAR(255) NOT NULL,
            usuario_id INT NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            KEY idx_ft_recurso (recurso_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,
        """
        CREATE TABLE IF NOT EXISTS forum_posts (
            id         INT AUTO_INCREMENT PRIMARY KEY,
            thread_id  INT NOT NULL,
            usuario_id INT NOT NULL,
            conteudo   TEXT NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            KEY idx_fp_thread (thread_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,
        """
        CREATE TABLE IF NOT EXISTS questionarios (
            id         INT AUTO_INCREMENT PRIMARY KEY,
            recurso_id INT NOT NULL UNIQUE,
            titulo     VARCHAR(255) NOT NULL,
            descricao  TEXT,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,
        """
        CREATE TABLE IF NOT EXISTS perguntas (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            questionario_id INT NOT NULL,
            enunciado       TEXT NOT NULL,
            tipo            VARCHAR(50) NOT NULL DEFAULT 'multipla_escolha',
            ordem           INT NOT NULL DEFAULT 0,
            KEY idx_pg_quiz (questionario_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,
        """
        CREATE TABLE IF NOT EXISTS opcoes_resposta (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            pergunta_id INT NOT NULL,
            texto       VARCHAR(500) NOT NULL,
            correta     TINYINT(1) NOT NULL DEFAULT 0,
            KEY idx_or_pergunta (pergunta_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,
        """
        CREATE TABLE IF NOT EXISTS tentativas_quiz (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            questionario_id INT NOT NULL,
            usuario_id      INT NOT NULL,
            nota            DECIMAL(5,2),
            iniciada_em     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            terminada_em    DATETIME,
            KEY idx_tq_usuario (usuario_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,
        """
        CREATE TABLE IF NOT EXISTS respostas_aluno (
            id            INT AUTO_INCREMENT PRIMARY KEY,
            tentativa_id  INT NOT NULL,
            pergunta_id   INT NOT NULL,
            opcao_id      INT,
            resposta_texto TEXT,
            KEY idx_ra_tentativa (tentativa_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,
        """
        CREATE TABLE IF NOT EXISTS activity_log (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id  INT NOT NULL,
            recurso_id  INT NOT NULL,
            tipo        VARCHAR(20) NOT NULL DEFAULT 'conclusao',
            created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            KEY idx_al_usuario (usuario_id),
            KEY idx_al_recurso (recurso_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,
        """
        CREATE TABLE IF NOT EXISTS mensagens (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            remetente_id    INT NOT NULL,
            destinatario_id INT NOT NULL,
            assunto         VARCHAR(255) NOT NULL,
            corpo           TEXT NOT NULL,
            lida            TINYINT(1) NOT NULL DEFAULT 0,
            created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            KEY idx_msg_dest (destinatario_id, lida),
            KEY idx_msg_rem (remetente_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """,
    ]
    for stmt in stmts:
        try:
            db.session.execute(text(stmt))
        except Exception as e:
            current_app.logger.warning("[student] _ensure_tables: %s", e)

    extra_alters = [
        "ALTER TABLE entregas ADD COLUMN IF NOT EXISTS recurso_id INT DEFAULT NULL",
        "ALTER TABLE entregas ADD COLUMN IF NOT EXISTS feedback TEXT NULL",
        "ALTER TABLE entregas ADD COLUMN IF NOT EXISTS data_avaliacao DATETIME NULL",
        "ALTER TABLE recursos_disciplina ADD COLUMN IF NOT EXISTS data_limite DATETIME NULL",
        "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS reset_token VARCHAR(100) NULL",
        "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS reset_token_expira DATETIME NULL",
    ]
    for stmt in extra_alters:
        try:
            db.session.execute(text(stmt))
        except Exception:
            pass
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()


# ──────────────────────────────────────────────
# PROGRESSO — concluir recurso (toggle)
# ──────────────────────────────────────────────

@student_bp.route("/cursos/recurso/<int:recurso_id>/concluir", methods=["POST"])
@login_required
def concluir_recurso(recurso_id):
    usuario_id = _current_usuario_id()
    if not usuario_id:
        abort(403)

    existing = _fetch_one(
        "SELECT id FROM recurso_conclusao WHERE usuario_id = :u AND recurso_id = :r",
        {"u": usuario_id, "r": recurso_id},
    )

    try:
        if existing:
            db.session.execute(
                text("DELETE FROM recurso_conclusao WHERE usuario_id = :u AND recurso_id = :r"),
                {"u": usuario_id, "r": recurso_id},
            )
        else:
            db.session.execute(
                text("""
                    INSERT INTO recurso_conclusao (usuario_id, recurso_id)
                    VALUES (:u, :r)
                    ON DUPLICATE KEY UPDATE completado_em = CURRENT_TIMESTAMP
                """),
                {"u": usuario_id, "r": recurso_id},
            )
            try:
                db.session.execute(
                    text("INSERT INTO activity_log (usuario_id, recurso_id, tipo) VALUES (:u, :r, 'conclusao')"),
                    {"u": usuario_id, "r": recurso_id},
                )
            except Exception:
                pass
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error("[student] concluir_recurso: %s", e, exc_info=True)

    next_url = request.form.get("next") or request.referrer or url_for("courses.ciclos")
    return redirect(next_url)


# ──────────────────────────────────────────────
# ENTREGAS — submeter ficheiro
# ──────────────────────────────────────────────

@student_bp.route("/cursos/recurso/<int:recurso_id>/entregar", methods=["POST"])
@login_required
def entregar_recurso(recurso_id):
    usuario_id = _current_usuario_id()
    if not usuario_id:
        abort(403)

    ficheiro = request.files.get("ficheiro")
    if not ficheiro or not ficheiro.filename:
        flash("Seleciona um ficheiro para entregar.", "warning")
        return redirect(request.referrer or url_for("courses.ciclos"))

    if not _allowed_upload(ficheiro.filename):
        flash("Tipo de ficheiro não permitido.", "danger")
        return redirect(request.referrer or url_for("courses.ciclos"))

    original_name = secure_filename(ficheiro.filename)
    ext = original_name.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"

    upload_root = current_app.config.get("UPLOAD_FOLDER") or os.path.join(
        current_app.root_path, "static", "uploads"
    )
    dest_folder = os.path.join(upload_root, "entregas", str(recurso_id))
    os.makedirs(dest_folder, exist_ok=True)

    dest_path = os.path.join(dest_folder, unique_name)
    ficheiro.save(dest_path)
    ficheiro_url = f"/static/uploads/entregas/{recurso_id}/{unique_name}"

    try:
        db.session.execute(
            text("""
                INSERT INTO entregas (tarefa_id, usuario_id, estado, ficheiro_url, data_entrega, recurso_id)
                VALUES (:tarefa_id, :usuario_id, 'entregue', :ficheiro_url, NOW(), :recurso_id)
            """),
            {
                "tarefa_id": recurso_id,
                "usuario_id": usuario_id,
                "ficheiro_url": ficheiro_url,
                "recurso_id": recurso_id,
            },
        )
        db.session.commit()
        try:
            db.session.execute(
                text("INSERT INTO activity_log (usuario_id, recurso_id, tipo) VALUES (:u, :r, 'entrega')"),
                {"u": usuario_id, "r": recurso_id},
            )
            db.session.commit()
        except Exception:
            pass
        flash("Entrega realizada com sucesso.", "success")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error("[student] entregar_recurso: %s", e, exc_info=True)
        flash("Erro ao registar a entrega.", "danger")

    next_url = request.form.get("next") or request.referrer or url_for("courses.ciclos")
    return redirect(next_url)


# ──────────────────────────────────────────────
# AS MINHAS ENTREGAS
# ──────────────────────────────────────────────

@student_bp.route("/as-minhas-entregas")
@login_required
def as_minhas_entregas():
    usuario_id = _current_usuario_id()
    usuario = get_current_user()

    entregas = _fetch_all("""
        SELECT
            e.id,
            e.estado,
            e.ficheiro_url,
            e.nota,
            e.feedback,
            e.data_entrega,
            e.recurso_id,
            r.titulo AS recurso_titulo,
            r.tipo   AS recurso_tipo,
            d.nombre AS disciplina_nome
        FROM entregas e
        LEFT JOIN recursos_disciplina r ON r.id = e.recurso_id
        LEFT JOIN secciones_disciplina s ON s.id = r.seccion_id
        LEFT JOIN disciplinas_ciclo d ON d.id = s.disciplina_id
        WHERE e.usuario_id = :uid
        ORDER BY e.data_entrega DESC
    """, {"uid": usuario_id})

    return render_template(
        "as_minhas_entregas.html",
        usuario=usuario,
        entregas=entregas,
    )


# ──────────────────────────────────────────────
# FÓRUM
# ──────────────────────────────────────────────

@student_bp.route("/forum/<int:recurso_id>", methods=["GET", "POST"])
@login_required
def forum(recurso_id):
    usuario_id = _current_usuario_id()
    usuario = get_current_user()

    recurso = _fetch_one(
        "SELECT id, titulo FROM recursos_disciplina WHERE id = :r",
        {"r": recurso_id},
    )
    if not recurso:
        abort(404)

    thread_id = request.args.get("thread", type=int)

    if request.method == "POST":
        action = request.form.get("action")

        if action == "novo_thread":
            titulo = request.form.get("titulo", "").strip()
            conteudo = request.form.get("conteudo", "").strip()
            if titulo and conteudo:
                try:
                    result = db.session.execute(
                        text("""
                            INSERT INTO forum_threads (recurso_id, titulo, usuario_id)
                            VALUES (:r, :titulo, :u)
                        """),
                        {"r": recurso_id, "titulo": titulo, "u": usuario_id},
                    )
                    new_thread_id = result.lastrowid
                    db.session.execute(
                        text("""
                            INSERT INTO forum_posts (thread_id, usuario_id, conteudo)
                            VALUES (:t, :u, :c)
                        """),
                        {"t": new_thread_id, "u": usuario_id, "c": conteudo},
                    )
                    db.session.commit()
                    flash("Tópico criado com sucesso.", "success")
                    return redirect(url_for("student.forum", recurso_id=recurso_id, thread=new_thread_id))
                except Exception as e:
                    db.session.rollback()
                    current_app.logger.error("[student] forum novo_thread: %s", e, exc_info=True)
                    flash("Erro ao criar o tópico.", "danger")
            else:
                flash("Título e mensagem são obrigatórios.", "warning")

        elif action == "novo_post":
            conteudo = request.form.get("conteudo", "").strip()
            if conteudo and thread_id:
                try:
                    db.session.execute(
                        text("""
                            INSERT INTO forum_posts (thread_id, usuario_id, conteudo)
                            VALUES (:t, :u, :c)
                        """),
                        {"t": thread_id, "u": usuario_id, "c": conteudo},
                    )
                    db.session.commit()
                    flash("Resposta publicada.", "success")
                    return redirect(url_for("student.forum", recurso_id=recurso_id, thread=thread_id))
                except Exception as e:
                    db.session.rollback()
                    current_app.logger.error("[student] forum novo_post: %s", e, exc_info=True)
                    flash("Erro ao publicar a resposta.", "danger")

        return redirect(url_for("student.forum", recurso_id=recurso_id, thread=thread_id))

    threads = _fetch_all("""
        SELECT
            ft.id,
            ft.titulo,
            ft.created_at,
            u.nome AS autor_nome,
            u.username AS autor_username,
            COUNT(fp.id) AS total_posts
        FROM forum_threads ft
        LEFT JOIN usuarios u ON u.id = ft.usuario_id
        LEFT JOIN forum_posts fp ON fp.thread_id = ft.id
        WHERE ft.recurso_id = :r
        GROUP BY ft.id, ft.titulo, ft.created_at, u.nome, u.username
        ORDER BY ft.created_at DESC
    """, {"r": recurso_id})

    posts = []
    thread_atual = None
    if thread_id:
        thread_atual = _fetch_one(
            "SELECT id, titulo, created_at FROM forum_threads WHERE id = :t AND recurso_id = :r",
            {"t": thread_id, "r": recurso_id},
        )
        if thread_atual:
            posts = _fetch_all("""
                SELECT
                    fp.id,
                    fp.conteudo,
                    fp.created_at,
                    u.nome AS autor_nome,
                    u.username AS autor_username
                FROM forum_posts fp
                LEFT JOIN usuarios u ON u.id = fp.usuario_id
                WHERE fp.thread_id = :t
                ORDER BY fp.created_at ASC
            """, {"t": thread_id})

    return render_template(
        "forum.html",
        usuario=usuario,
        recurso=recurso,
        threads=threads,
        thread_atual=thread_atual,
        posts=posts,
        thread_id=thread_id,
    )


# ──────────────────────────────────────────────
# QUIZ
# ──────────────────────────────────────────────

def _quiz_context(recurso_id):
    """Recurso + questionario associados, ou (None, None) se não existirem."""
    recurso = _fetch_one(
        "SELECT id, titulo FROM recursos_disciplina WHERE id = :r",
        {"r": recurso_id},
    )
    if not recurso:
        return None, None
    questionario = _fetch_one(
        "SELECT id, titulo, descricao FROM questionarios WHERE recurso_id = :r",
        {"r": recurso_id},
    )
    return recurso, questionario


def _tentativa_aberta(questionario_id, usuario_id):
    return _fetch_one(
        """SELECT id, iniciada_em FROM tentativas_quiz
           WHERE questionario_id = :q AND usuario_id = :u AND terminada_em IS NULL
           ORDER BY iniciada_em DESC LIMIT 1""",
        {"q": questionario_id, "u": usuario_id},
    )


@student_bp.route("/quiz/<int:recurso_id>")
@login_required
def quiz(recurso_id):
    usuario = get_current_user()
    usuario_id = _current_usuario_id()

    recurso, questionario = _quiz_context(recurso_id)
    if not recurso:
        abort(404)

    n_perguntas = 0
    tentativas = []
    aberta = None
    if questionario:
        row = _fetch_one(
            "SELECT COUNT(*) AS n FROM perguntas WHERE questionario_id = :q",
            {"q": questionario["id"]},
        )
        n_perguntas = (row["n"] if row else 0) or 0

        tentativas = _fetch_all(
            """SELECT id, nota, iniciada_em, terminada_em
               FROM tentativas_quiz
               WHERE questionario_id = :q AND usuario_id = :u
               ORDER BY iniciada_em DESC LIMIT 10""",
            {"q": questionario["id"], "u": usuario_id},
        )
        aberta = _tentativa_aberta(questionario["id"], usuario_id)

    melhor_nota = None
    notas = [t["nota"] for t in tentativas if t["nota"] is not None]
    if notas:
        melhor_nota = max(notas)

    return render_template(
        "quiz.html",
        usuario=usuario,
        recurso=recurso,
        questionario=questionario,
        n_perguntas=n_perguntas,
        tentativas=tentativas,
        tentativa_aberta=aberta,
        melhor_nota=melhor_nota,
    )


@student_bp.route("/quiz/<int:recurso_id>/iniciar", methods=["POST"])
@login_required
def quiz_iniciar(recurso_id):
    usuario_id = _current_usuario_id()
    recurso, questionario = _quiz_context(recurso_id)
    if not recurso or not questionario:
        abort(404)

    row = _fetch_one(
        "SELECT COUNT(*) AS n FROM perguntas WHERE questionario_id = :q",
        {"q": questionario["id"]},
    )
    if not row or not row["n"]:
        flash("Este questionário ainda não tem perguntas.", "warning")
        return redirect(url_for("student.quiz", recurso_id=recurso_id))

    # Reaproveita a tentativa aberta se existir; senão cria uma nova
    if not _tentativa_aberta(questionario["id"], usuario_id):
        try:
            db.session.execute(
                text("""INSERT INTO tentativas_quiz (questionario_id, usuario_id)
                        VALUES (:q, :u)"""),
                {"q": questionario["id"], "u": usuario_id},
            )
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error("[student] quiz_iniciar: %s", e, exc_info=True)
            flash("Erro ao iniciar o questionário.", "danger")
            return redirect(url_for("student.quiz", recurso_id=recurso_id))

    return redirect(url_for("student.quiz_responder", recurso_id=recurso_id))


@student_bp.route("/quiz/<int:recurso_id>/responder")
@login_required
def quiz_responder(recurso_id):
    usuario = get_current_user()
    usuario_id = _current_usuario_id()
    recurso, questionario = _quiz_context(recurso_id)
    if not recurso or not questionario:
        abort(404)

    tentativa = _tentativa_aberta(questionario["id"], usuario_id)
    if not tentativa:
        return redirect(url_for("student.quiz", recurso_id=recurso_id))

    perguntas = _fetch_all(
        """SELECT id, enunciado, tipo, ordem FROM perguntas
           WHERE questionario_id = :q ORDER BY ordem ASC, id ASC""",
        {"q": questionario["id"]},
    )
    opcoes = _fetch_all(
        """SELECT o.id, o.pergunta_id, o.texto
           FROM opcoes_resposta o
           JOIN perguntas p ON p.id = o.pergunta_id
           WHERE p.questionario_id = :q
           ORDER BY o.id ASC""",
        {"q": questionario["id"]},
    )
    opcoes_por_pergunta = {}
    for o in opcoes:
        opcoes_por_pergunta.setdefault(o["pergunta_id"], []).append(o)

    return render_template(
        "quiz_responder.html",
        usuario=usuario,
        recurso=recurso,
        questionario=questionario,
        tentativa=tentativa,
        perguntas=perguntas,
        opcoes_por_pergunta=opcoes_por_pergunta,
    )


@student_bp.route("/quiz/<int:recurso_id>/submeter", methods=["POST"])
@login_required
def quiz_submeter(recurso_id):
    usuario_id = _current_usuario_id()
    recurso, questionario = _quiz_context(recurso_id)
    if not recurso or not questionario:
        abort(404)

    tentativa = _tentativa_aberta(questionario["id"], usuario_id)
    if not tentativa:
        flash("Não há nenhuma tentativa em curso.", "warning")
        return redirect(url_for("student.quiz", recurso_id=recurso_id))

    perguntas = _fetch_all(
        "SELECT id FROM perguntas WHERE questionario_id = :q",
        {"q": questionario["id"]},
    )
    corretas_rows = _fetch_all(
        """SELECT o.pergunta_id, o.id
           FROM opcoes_resposta o
           JOIN perguntas p ON p.id = o.pergunta_id
           WHERE p.questionario_id = :q AND o.correta = 1""",
        {"q": questionario["id"]},
    )
    corretas = {r["pergunta_id"]: r["id"] for r in corretas_rows}

    total = len(perguntas)
    acertos = 0
    try:
        for p in perguntas:
            escolhida = request.form.get(f"pergunta_{p['id']}", type=int)
            db.session.execute(
                text("""INSERT INTO respostas_aluno (tentativa_id, pergunta_id, opcao_id)
                        VALUES (:t, :p, :o)"""),
                {"t": tentativa["id"], "p": p["id"], "o": escolhida},
            )
            if escolhida and corretas.get(p["id"]) == escolhida:
                acertos += 1

        nota = round(acertos / total * 20, 1) if total else 0
        db.session.execute(
            text("""UPDATE tentativas_quiz
                    SET nota = :n, terminada_em = NOW()
                    WHERE id = :t"""),
            {"n": nota, "t": tentativa["id"]},
        )
        db.session.execute(
            text("INSERT INTO activity_log (usuario_id, recurso_id, tipo) VALUES (:u, :r, 'quiz')"),
            {"u": usuario_id, "r": recurso_id},
        )
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error("[student] quiz_submeter: %s", e, exc_info=True)
        flash("Erro ao submeter o questionário.", "danger")
        return redirect(url_for("student.quiz", recurso_id=recurso_id))

    return redirect(url_for(
        "student.quiz_resultado", recurso_id=recurso_id, tentativa_id=tentativa["id"]
    ))


@student_bp.route("/quiz/<int:recurso_id>/resultado/<int:tentativa_id>")
@login_required
def quiz_resultado(recurso_id, tentativa_id):
    usuario = get_current_user()
    usuario_id = _current_usuario_id()
    recurso, questionario = _quiz_context(recurso_id)
    if not recurso or not questionario:
        abort(404)

    tentativa = _fetch_one(
        """SELECT id, nota, iniciada_em, terminada_em FROM tentativas_quiz
           WHERE id = :t AND usuario_id = :u AND questionario_id = :q""",
        {"t": tentativa_id, "u": usuario_id, "q": questionario["id"]},
    )
    if not tentativa or tentativa["terminada_em"] is None:
        return redirect(url_for("student.quiz", recurso_id=recurso_id))

    revisao = _fetch_all(
        """SELECT
               p.id            AS pergunta_id,
               p.enunciado,
               ra.opcao_id     AS escolhida_id,
               oe.texto        AS escolhida_texto,
               oc.id           AS correta_id,
               oc.texto        AS correta_texto
           FROM perguntas p
           LEFT JOIN respostas_aluno ra
                  ON ra.pergunta_id = p.id AND ra.tentativa_id = :t
           LEFT JOIN opcoes_resposta oe ON oe.id = ra.opcao_id
           LEFT JOIN opcoes_resposta oc
                  ON oc.pergunta_id = p.id AND oc.correta = 1
           WHERE p.questionario_id = :q
           ORDER BY p.ordem ASC, p.id ASC""",
        {"t": tentativa_id, "q": questionario["id"]},
    )

    acertos = sum(1 for r in revisao if r["escolhida_id"] and r["escolhida_id"] == r["correta_id"])

    return render_template(
        "quiz_resultado.html",
        usuario=usuario,
        recurso=recurso,
        questionario=questionario,
        tentativa=tentativa,
        revisao=revisao,
        acertos=acertos,
        total=len(revisao),
    )

"""
Blueprint: Mensageria interna.
Rutas: /mensagens            → caixa de entrada
       /mensagens/enviadas   → mensagens enviadas
       /mensagens/nova       → compor mensagem
       /mensagens/<id>       → ler mensagem (marca como lida) + responder
"""

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

from extensions import db
from decorators import login_required
from services.data_service import get_current_user

messages_bp = Blueprint("messages", __name__)


def _fetch_one(sql, params=None):
    try:
        return db.session.execute(text(sql), params or {}).mappings().first()
    except Exception as e:
        current_app.logger.error("[messages] _fetch_one: %s", e, exc_info=True)
        return None


def _fetch_all(sql, params=None):
    try:
        return db.session.execute(text(sql), params or {}).mappings().all()
    except Exception as e:
        current_app.logger.error("[messages] _fetch_all: %s", e, exc_info=True)
        return []


def _uid():
    return session.get("usuario_id")


def _destinatarios_possiveis(usuario_id):
    """Todos os utilizadores ativos exceto o próprio, com os seus roles."""
    return _fetch_all("""
        SELECT
            u.id,
            u.nome,
            u.apelido,
            u.username,
            COALESCE(GROUP_CONCAT(r.nombre SEPARATOR ', '), '') AS roles
        FROM usuarios u
        LEFT JOIN usuario_roles ur ON ur.usuario_id = u.id
        LEFT JOIN roles r ON r.id = ur.rol_id
        WHERE u.activo = 1 AND u.id != :uid
        GROUP BY u.id, u.nome, u.apelido, u.username
        ORDER BY u.nome ASC, u.username ASC
    """, {"uid": usuario_id})


def contar_nao_lidas(usuario_id):
    """Nº de mensagens não lidas — usado pelo context processor do layout."""
    if not usuario_id:
        return 0
    row = _fetch_one(
        "SELECT COUNT(*) AS n FROM mensagens WHERE destinatario_id = :u AND lida = 0",
        {"u": usuario_id},
    )
    return (row["n"] if row else 0) or 0


@messages_bp.route("/mensagens")
@login_required
def inbox():
    usuario = get_current_user()
    usuario_id = _uid()

    mensagens = _fetch_all("""
        SELECT
            m.id, m.assunto, m.corpo, m.lida, m.created_at,
            u.nome     AS remetente_nome,
            u.username AS remetente_username
        FROM mensagens m
        LEFT JOIN usuarios u ON u.id = m.remetente_id
        WHERE m.destinatario_id = :u
        ORDER BY m.created_at DESC
        LIMIT 200
    """, {"u": usuario_id})

    return render_template(
        "mensagens.html",
        usuario=usuario,
        mensagens=mensagens,
        vista="recebidas",
        nao_lidas=sum(1 for m in mensagens if not m["lida"]),
    )


@messages_bp.route("/mensagens/enviadas")
@login_required
def enviadas():
    usuario = get_current_user()
    usuario_id = _uid()

    mensagens = _fetch_all("""
        SELECT
            m.id, m.assunto, m.corpo, m.lida, m.created_at,
            u.nome     AS destinatario_nome,
            u.username AS destinatario_username
        FROM mensagens m
        LEFT JOIN usuarios u ON u.id = m.destinatario_id
        WHERE m.remetente_id = :u
        ORDER BY m.created_at DESC
        LIMIT 200
    """, {"u": usuario_id})

    return render_template(
        "mensagens.html",
        usuario=usuario,
        mensagens=mensagens,
        vista="enviadas",
        nao_lidas=None,
    )


@messages_bp.route("/mensagens/nova", methods=["GET", "POST"])
@login_required
def nova():
    usuario = get_current_user()
    usuario_id = _uid()

    if request.method == "POST":
        destinatario_id = request.form.get("destinatario_id", type=int)
        assunto = (request.form.get("assunto") or "").strip()
        corpo = (request.form.get("corpo") or "").strip()

        if not destinatario_id or not assunto or not corpo:
            flash("Destinatário, assunto e mensagem são obrigatórios.", "warning")
            return redirect(url_for("messages.nova"))

        dest = _fetch_one(
            "SELECT id, nome, username FROM usuarios WHERE id = :d AND activo = 1",
            {"d": destinatario_id},
        )
        if not dest or destinatario_id == usuario_id:
            flash("Destinatário inválido.", "danger")
            return redirect(url_for("messages.nova"))

        try:
            db.session.execute(
                text("""INSERT INTO mensagens (remetente_id, destinatario_id, assunto, corpo)
                        VALUES (:r, :d, :a, :c)"""),
                {"r": usuario_id, "d": destinatario_id, "a": assunto, "c": corpo},
            )
            # Notificação para o destinatário (best effort)
            try:
                remetente_nome = (usuario or {}).get("nome") or session.get("usuario_nome") or "Utilizador"
                db.session.execute(
                    text("""INSERT INTO notificacoes (usuario_id, titulo, mensagem, tipo)
                            VALUES (:u, :t, :m, 'info')"""),
                    {"u": destinatario_id,
                     "t": f"Nova mensagem de {remetente_nome}",
                     "m": assunto},
                )
            except Exception:
                pass
            db.session.commit()
            flash("Mensagem enviada.", "success")
            return redirect(url_for("messages.inbox"))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error("[messages] nova: %s", e, exc_info=True)
            flash("Erro ao enviar a mensagem.", "danger")
            return redirect(url_for("messages.nova"))

    destinatarios = _destinatarios_possiveis(usuario_id)
    para = request.args.get("para", type=int)
    assunto_inicial = request.args.get("assunto", "")

    return render_template(
        "mensagem_nova.html",
        usuario=usuario,
        destinatarios=destinatarios,
        para=para,
        assunto_inicial=assunto_inicial,
    )


@messages_bp.route("/mensagens/<int:mensagem_id>")
@login_required
def detalhe(mensagem_id):
    usuario = get_current_user()
    usuario_id = _uid()

    mensagem = _fetch_one("""
        SELECT
            m.id, m.assunto, m.corpo, m.lida, m.created_at,
            m.remetente_id, m.destinatario_id,
            ur.nome     AS remetente_nome,
            ur.username AS remetente_username,
            ud.nome     AS destinatario_nome,
            ud.username AS destinatario_username
        FROM mensagens m
        LEFT JOIN usuarios ur ON ur.id = m.remetente_id
        LEFT JOIN usuarios ud ON ud.id = m.destinatario_id
        WHERE m.id = :id
          AND (m.destinatario_id = :u OR m.remetente_id = :u)
    """, {"id": mensagem_id, "u": usuario_id})

    if not mensagem:
        abort(404)

    if mensagem["destinatario_id"] == usuario_id and not mensagem["lida"]:
        try:
            db.session.execute(
                text("UPDATE mensagens SET lida = 1 WHERE id = :id"),
                {"id": mensagem_id},
            )
            db.session.commit()
        except Exception:
            db.session.rollback()

    return render_template(
        "mensagem_detalhe.html",
        usuario=usuario,
        m=mensagem,
        sou_destinatario=(mensagem["destinatario_id"] == usuario_id),
    )

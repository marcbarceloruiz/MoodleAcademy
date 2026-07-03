"""
Blueprint: Autenticação de utilizadores.
Rotas: /login  /logout  /acesso-negado

Convive com o login admin legacy (ADMIN_PASSWORD em /admin/login).
Não altera admin_routes.py.

SESSÃO:
    session["usuario_id"]       → int
    session["usuario_username"] → str
    session["usuario_nome"]     → str
    session["usuario_roles"]    → list[str]
    session["admin_ok"]         → True  (se role admin — compatibilidade)
"""

import secrets
from datetime import datetime, timedelta

from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, flash, current_app,
)
from sqlalchemy import text
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db, mail
from flask_mail import Message

auth_bp = Blueprint("auth", __name__)


# ─── helpers ─────────────────────────────────────────────────

def _get_user(username: str):
    """Devolve dict do utilizador activo ou None."""
    try:
        row = db.session.execute(
            text("""
                SELECT id, username, email, password_hash, nome, apelido
                FROM usuarios
                WHERE username = :u AND activo = 1
                LIMIT 1
            """),
            {"u": username},
        ).mappings().first()
        return dict(row) if row else None
    except Exception as e:
        print("auth._get_user error:", e)
        return None


def _get_roles(usuario_id: int) -> list:
    """Devolve lista de strings com os roles do utilizador."""
    try:
        rows = db.session.execute(
            text("""
                SELECT r.nombre
                FROM roles r
                JOIN usuario_roles ur ON ur.rol_id = r.id
                WHERE ur.usuario_id = :uid
            """),
            {"uid": usuario_id},
        ).fetchall()
        return [r[0] for r in rows]
    except Exception as e:
        print("auth._get_roles error:", e)
        return []


def _do_login(user: dict, roles: list):
    """Grava dados de sessão. Ativa admin_ok se role admin."""
    session.permanent = False
    session["usuario_id"]       = user["id"]
    session["usuario_username"] = user["username"]
    session["usuario_nome"]     = user.get("nome") or user["username"]
    session["usuario_roles"]    = roles
    # Compatibilidade com admin_routes before_request
    if "admin" in roles:
        session["admin_ok"] = True


def _do_logout():
    """Remove todos os dados de sessão (novo sistema + legacy)."""
    for key in ("usuario_id", "usuario_username", "usuario_nome",
                "usuario_roles", "admin_ok"):
        session.pop(key, None)


# ─── rotas ───────────────────────────────────────────────────

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # Já autenticado → redirigir
    if "usuario_id" in session or session.get("admin_ok"):
        return redirect(url_for("dashboard.dashboard"))

    error    = None
    next_url = request.args.get("next") or request.form.get("next", "")

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            error = "Preenche o utilizador e a palavra-passe."
        else:
            user = _get_user(username)
            if user and check_password_hash(user["password_hash"], password):
                roles = _get_roles(user["id"])
                _do_login(user, roles)
                flash(f"Bem-vindo, {user.get('nome') or username}!", "success")

                if next_url and next_url.startswith("/"):
                    return redirect(next_url)
                if "admin" in roles:
                    return redirect(url_for("admin.admin"))
                if "docente" in roles:
                    return redirect(url_for("portal.portal_area",
                                            area_slug="area-docente"))
                return redirect(url_for("dashboard.dashboard"))
            else:
                error = "Utilizador ou palavra-passe incorretos."

    return render_template("login.html", error=error, next=next_url)


@auth_bp.route("/logout", methods=["POST"])
def logout():
    nome = session.get("usuario_nome") or "utilizador"
    _do_logout()
    flash(f"Sessão terminada. Até logo, {nome}!", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/acesso-negado")
def acesso_negado():
    from services.data_service import get_current_user
    return render_template("403.html", usuario=get_current_user()), 403


# ─── reset de palavra-passe ──────────────────────────────────

@auth_bp.route("/meu-perfil", methods=["GET", "POST"])
def meu_perfil():
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return redirect(url_for("auth.login"))

    row = db.session.execute(
        text("SELECT id, username, email, nome, apelido FROM usuarios WHERE id = :id LIMIT 1"),
        {"id": usuario_id},
    ).mappings().first()

    if not row:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        action = request.form.get("action", "perfil")

        if action == "perfil":
            nome    = request.form.get("nome", "").strip()
            apelido = request.form.get("apelido", "").strip()
            try:
                db.session.execute(
                    text("UPDATE usuarios SET nome = :n, apelido = :a WHERE id = :id"),
                    {"n": nome, "a": apelido, "id": usuario_id},
                )
                db.session.commit()
                session["usuario_nome"] = nome or row["username"]
                flash("Perfil atualizado com sucesso.", "success")
            except Exception as e:
                db.session.rollback()
                current_app.logger.error("[auth] meu_perfil update: %s", e)
                flash("Erro ao atualizar o perfil.", "danger")

        elif action == "password":
            atual    = request.form.get("password_atual", "")
            nova     = request.form.get("password_nova", "")
            nova2    = request.form.get("password_nova2", "")
            user_row = db.session.execute(
                text("SELECT password_hash FROM usuarios WHERE id = :id"),
                {"id": usuario_id},
            ).mappings().first()

            if not user_row or not check_password_hash(user_row["password_hash"], atual):
                flash("Palavra-passe atual incorreta.", "danger")
            elif len(nova) < 8:
                flash("A nova palavra-passe deve ter pelo menos 8 caracteres.", "warning")
            elif nova != nova2:
                flash("As palavras-passe não coincidem.", "warning")
            else:
                try:
                    db.session.execute(
                        text("UPDATE usuarios SET password_hash = :h WHERE id = :id"),
                        {"h": generate_password_hash(nova), "id": usuario_id},
                    )
                    db.session.commit()
                    flash("Palavra-passe alterada com sucesso.", "success")
                except Exception as e:
                    db.session.rollback()
                    current_app.logger.error("[auth] meu_perfil password: %s", e)
                    flash("Erro ao alterar a palavra-passe.", "danger")

        return redirect(url_for("auth.meu_perfil"))

    # Estatísticas do aluno
    stats = {"recursos_concluidos": 0, "entregas": 0}
    try:
        stats["recursos_concluidos"] = db.session.execute(
            text("SELECT COUNT(*) FROM recurso_conclusao WHERE usuario_id = :id"),
            {"id": usuario_id},
        ).scalar() or 0
        stats["entregas"] = db.session.execute(
            text("SELECT COUNT(*) FROM entregas WHERE usuario_id = :id"),
            {"id": usuario_id},
        ).scalar() or 0
    except Exception:
        pass

    return render_template("meu_perfil.html", usuario=dict(row), stats=stats)


@auth_bp.route("/esqueci-password", methods=["GET", "POST"])
def esqueci_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        if not email:
            flash("Introduz o teu endereço de email.", "warning")
            return redirect(url_for("auth.esqueci_password"))

        row = db.session.execute(
            text("SELECT id, nome FROM usuarios WHERE email = :e AND activo = 1 LIMIT 1"),
            {"e": email},
        ).mappings().first()

        # Resposta genérica — não revelamos se o email existe
        flash("Se esse email está registado, receberás um link em breve.", "info")

        if row:
            token  = secrets.token_urlsafe(32)
            expira = datetime.now() + timedelta(hours=1)
            try:
                db.session.execute(
                    text("""
                        UPDATE usuarios
                        SET reset_token = :t, reset_token_expira = :e
                        WHERE id = :id
                    """),
                    {"t": token, "e": expira, "id": row["id"]},
                )
                db.session.commit()

                reset_url = url_for("auth.reset_password", token=token, _external=True)
                nome = row["nome"] or "Utilizador"
                html = f"""
                <div style="font-family:sans-serif;max-width:480px;margin:0 auto;color:#1a1a2e">
                  <div style="background:#1a1a2e;padding:20px 24px;border-radius:8px 8px 0 0">
                    <h2 style="color:#fff;margin:0;font-size:18px">Academia Profissional</h2>
                    <p style="color:#94a3b8;margin:4px 0 0;font-size:12px">Campus Virtual</p>
                  </div>
                  <div style="background:#f8fafc;padding:24px;border-radius:0 0 8px 8px;border:1px solid #e2e8f0">
                    <p style="margin:0 0 16px">Olá <strong>{nome}</strong>,</p>
                    <p style="margin:0 0 20px">Recebemos um pedido de redefinição de palavra-passe.
                       Clica no botão abaixo para criar uma nova. O link expira em <strong>1 hora</strong>.</p>
                    <a href="{reset_url}"
                       style="display:inline-block;background:#1a1a2e;color:#fff;padding:12px 24px;
                              border-radius:6px;text-decoration:none;font-size:14px;font-weight:600">
                      Redefinir palavra-passe
                    </a>
                    <p style="margin:20px 0 0;font-size:11px;color:#94a3b8">
                      Se não fizeste este pedido, podes ignorar este email.<br>
                      Campus Virtual — Academia Profissional Prof. Albino de Matos
                    </p>
                  </div>
                </div>
                """
                msg = Message(
                    subject="Redefinição de palavra-passe — Campus Virtual",
                    recipients=[email],
                    html=html,
                )
                mail.send(msg)
            except Exception as e:
                db.session.rollback()
                current_app.logger.error("[auth] esqueci_password: %s", e, exc_info=True)

        return redirect(url_for("auth.login"))

    return render_template("esqueci_password.html")


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    row = db.session.execute(
        text("""
            SELECT id, nome, reset_token_expira
            FROM usuarios
            WHERE reset_token = :t AND activo = 1
            LIMIT 1
        """),
        {"t": token},
    ).mappings().first()

    if not row or row["reset_token_expira"] < datetime.now():
        flash("O link de redefinição é inválido ou já expirou.", "danger")
        return redirect(url_for("auth.esqueci_password"))

    if request.method == "POST":
        password  = request.form.get("password", "")
        password2 = request.form.get("password2", "")

        if len(password) < 8:
            flash("A palavra-passe deve ter pelo menos 8 caracteres.", "warning")
            return render_template("reset_password.html", token=token)
        if password != password2:
            flash("As palavras-passe não coincidem.", "warning")
            return render_template("reset_password.html", token=token)

        try:
            db.session.execute(
                text("""
                    UPDATE usuarios
                    SET password_hash      = :h,
                        reset_token        = NULL,
                        reset_token_expira = NULL
                    WHERE id = :id
                """),
                {"h": generate_password_hash(password), "id": row["id"]},
            )
            db.session.commit()
            flash("Palavra-passe alterada com sucesso. Podes entrar agora.", "success")
            return redirect(url_for("auth.login"))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error("[auth] reset_password: %s", e, exc_info=True)
            flash("Erro ao atualizar a palavra-passe.", "danger")

    return render_template("reset_password.html", token=token)

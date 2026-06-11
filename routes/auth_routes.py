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

from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, flash,
)
from sqlalchemy import text
from werkzeug.security import check_password_hash

from extensions import db

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

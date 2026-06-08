"""
decorators.py
=============
Academia Profissional Prof. Albino de Matos — Escola Profissional Vértice

Decoradores de autenticação e autorização por roles.
Compatível com o login legacy por ADMIN_PASSWORD.

USO:
    from decorators import login_required, role_required

    @app.route('/profile')
    @login_required
    def profile(): ...

    @app.route('/area-docente')
    @role_required('admin', 'docente')
    def area_docente(): ...
"""

from functools import wraps
from flask import session, redirect, url_for, flash, request


def _is_authenticated():
    """Qualquer utilizador autenticado (novo sistema ou legacy admin)."""
    return (
        "usuario_id" in session
        or session.get("admin_ok") is True
    )


def _has_role(*allowed_roles):
    """
    True se o utilizador tem pelo menos um dos roles indicados.
    Suporta o sistema novo (session['usuario_roles']) e o legado (admin_ok).
    """
    # Legacy: ADMIN_PASSWORD → role admin implícito
    if session.get("admin_ok") is True and "admin" in allowed_roles:
        return True

    user_roles = session.get("usuario_roles", [])
    return any(r in user_roles for r in allowed_roles)


def login_required(f):
    """Exige utilizador autenticado. Redirige para /login se não estiver."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not _is_authenticated():
            flash("Precisas de iniciar sessão para aceder a esta página.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        return f(*args, **kwargs)
    return decorated


def role_required(*allowed_roles):
    """
    Exige utilizador autenticado + ter um dos roles indicados.
    Redirige para /acesso-negado se não tiver permissão.
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not _is_authenticated():
                flash("Precisas de iniciar sessão para aceder a esta página.", "warning")
                return redirect(url_for("auth.login", next=request.path))
            if not _has_role(*allowed_roles):
                flash("Não tens permissão para aceder a esta área.", "danger")
                return redirect(url_for("auth.acesso_negado"))
            return f(*args, **kwargs)
        return decorated
    return decorator

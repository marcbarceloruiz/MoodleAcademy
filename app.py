"""
Academia Profissional Prof. Albino de Matos - Escola Profissional Vértice
Campus Virtual — Ponto de entrada Flask.
"""

from flask import Flask, session
from flask_wtf.csrf import CSRFProtect
from config import Config
from extensions import db, migrate

csrf = CSRFProtect()

from routes.dashboard_routes import dashboard_bp
from routes.courses_routes   import courses_bp
from routes.admin_routes     import admin_bp
from routes.portal_routes    import portal_bp
from routes.auth_routes      import auth_bp
from routes.student_routes   import student_bp

from services.data_service import (
    get_user_courses,
    get_events,
    calculate_course_progress,
    format_date_short,
)
from models import Centro


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # ── Context processor: dados de layout e sidebar ──────────
    @app.context_processor
    def inject_layout_data():
        try:
            layout_mis_cursos = get_user_courses()
            for c in layout_mis_cursos:
                c["_progreso"] = calculate_course_progress(c)
            layout_eventos = get_events(limit=3)
            for e in layout_eventos:
                e["_fecha_corta"] = format_date_short(e["fecha"])
        except Exception as e:
            app.logger.warning("inject_layout_data: cursos/eventos: %s", e)
            layout_mis_cursos = []
            layout_eventos    = []
        try:
            from services.moodle_service import get_notificacoes_usuario
            from flask import session as _s
            layout_notificacoes = get_notificacoes_usuario(
                _s.get("usuario_id"), limit=6)
        except Exception as e:
            app.logger.warning("inject_layout_data: notificacoes: %s", e)
            layout_notificacoes = []

        return {
            "layout_mis_cursos": layout_mis_cursos,
            "layout_eventos":    layout_eventos,
            "layout_notificacoes": layout_notificacoes,
        }

    # ── Context processor: dados de sessão para templates ─────
    @app.context_processor
    def inject_session_data():
        """
        Disponibiliza variáveis de sessão em todos os templates:
          session_autenticado   → bool
          session_is_admin      → bool
          session_is_docente    → bool
          session_is_aluno      → bool
          session_usuario_nome  → str
          session_roles         → list[str]
        """
        roles        = session.get("usuario_roles", [])
        legacy_admin = session.get("admin_ok") is True
        autenticado  = bool(session.get("usuario_id")) or legacy_admin

        return {
            "session_autenticado":      autenticado,
            "session_is_admin":         ("admin" in roles) or legacy_admin,
            "session_is_docente":       "docente" in roles,
            "session_is_aluno":         "aluno"   in roles,
            "session_usuario_nome":     session.get("usuario_nome", ""),
            "session_usuario_username": session.get("usuario_username", ""),
            "session_roles":            roles,
        }

    # ── Rota de diagnóstico (apenas em DEBUG) ─────────────────
    if app.config.get("DEBUG", False):
        @app.route("/db-test")
        def db_test():
            try:
                centro = Centro.query.first()
                if not centro:
                    return "<h1>MySQL OK</h1><p>Tabela centro sem dados.</p>"
                return (f"<h1>MySQL OK</h1><h2>{centro.nome_oficial}</h2>"
                        f"<p>{centro.cidade}, {centro.pais}</p>")
            except Exception as e:
                return f"<h1>Erro MySQL</h1><pre>{e}</pre>", 500

    # ── Registar blueprints ───────────────────────────────────
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(portal_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)

    with app.app_context():
        from routes.student_routes import _ensure_tables
        _ensure_tables()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=app.config.get("DEBUG", False))

"""
Academia Profissional Prof. Albino de Matos - Escola Profissional Vértice
Campus Virtual — Ponto de entrada Flask.
"""

from flask import Flask, session
from config import Config
from extensions import db, migrate

from routes.dashboard_routes import dashboard_bp
from routes.courses_routes   import courses_bp
from routes.admin_routes     import admin_bp
from routes.portal_routes    import portal_bp
from routes.auth_routes      import auth_bp

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
        except Exception:
            layout_mis_cursos = []
            layout_eventos    = []
        return {
            "layout_mis_cursos": layout_mis_cursos,
            "layout_eventos":    layout_eventos,
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

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=app.config.get("DEBUG", False))

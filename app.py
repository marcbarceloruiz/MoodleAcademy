"""
Academia Vertice — Campus Virtual
Punto de entrada principal de la aplicación Flask.
"""

from flask import Flask
from config import Config
from routes.dashboard_routes import dashboard_bp
from routes.courses_routes import courses_bp
from routes.admin_routes import admin_bp
from routes.portal_routes import portal_bp
from services.data_service import get_user_courses, get_events, calculate_course_progress, format_date_short


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    @app.context_processor
    def inject_layout_data():
        """Datos comunes para el layout y el sidebar."""
        layout_mis_cursos = get_user_courses()
        for curso in layout_mis_cursos:
            curso['_progreso'] = calculate_course_progress(curso)

        layout_eventos = get_events(limit=3)
        for evento in layout_eventos:
            evento['_fecha_corta'] = format_date_short(evento['fecha'])

        return {
            'layout_mis_cursos': layout_mis_cursos,
            'layout_eventos': layout_eventos,
        }

    # Registro de Blueprints
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(portal_bp)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

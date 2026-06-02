"""
Academia Profissional Prof. Albino de Matos - Escola Profissional Vértice
Campus Virtual

Punto de entrada principal de la aplicación Flask.
"""

from flask import Flask
from config import Config
from extensions import db, migrate

from routes.dashboard_routes import dashboard_bp
from routes.courses_routes import courses_bp
from routes.admin_routes import admin_bp
from routes.portal_routes import portal_bp

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

    # Base de datos y migraciones
    db.init_app(app)
    migrate.init_app(app, db)

    @app.context_processor
    def inject_layout_data():
        """Datos comunes para el layout y el sidebar."""
        layout_mis_cursos = get_user_courses()
        for curso in layout_mis_cursos:
            curso["_progreso"] = calculate_course_progress(curso)

        layout_eventos = get_events(limit=3)
        for evento in layout_eventos:
            evento["_fecha_corta"] = format_date_short(evento["fecha"])

        return {
            "layout_mis_cursos": layout_mis_cursos,
            "layout_eventos": layout_eventos,
        }

    # Ruta temporal para comprobar conexión con MySQL
    @app.route("/db-test")
    def db_test():
        centro = Centro.query.first()

        if not centro:
            return """
            <h1>Conexión correcta, pero no hay datos en la tabla centro</h1>
            <p>Revisa que hayas hecho el INSERT en MySQL.</p>
            """

        return f"""
        <h1>{centro.nome_oficial}</h1>
        <p><strong>Nombre corto:</strong> {centro.nome_curto}</p>
        <p><strong>Ubicación:</strong> {centro.cidade}, {centro.pais}</p>
        """

    # Registro de Blueprints
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(portal_bp)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
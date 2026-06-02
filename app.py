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

    # Inicializar base de datos y migraciones
    db.init_app(app)
    migrate.init_app(app, db)

    @app.context_processor
    def inject_layout_data():
        """
        Datos comunes para el layout y el sidebar.

        De momento estos datos pueden venir del data_service.
        Más adelante los conectaremos completamente a MySQL.
        """
        try:
            layout_mis_cursos = get_user_courses()

            for curso in layout_mis_cursos:
                curso["_progreso"] = calculate_course_progress(curso)

            layout_eventos = get_events(limit=3)

            for evento in layout_eventos:
                evento["_fecha_corta"] = format_date_short(evento["fecha"])

        except Exception:
            # Evita que toda la web se caiga si falla algún dato del sidebar
            layout_mis_cursos = []
            layout_eventos = []

        return {
            "layout_mis_cursos": layout_mis_cursos,
            "layout_eventos": layout_eventos,
        }

    @app.route("/db-test")
    def db_test():
        """
        Ruta temporal para comprobar que Flask conecta correctamente con MySQL.
        """
        try:
            centro = Centro.query.first()

            if not centro:
                return """
                <h1>Conexión correcta con MySQL</h1>
                <p>Pero no hay datos en la tabla <strong>centro</strong>.</p>
                <p>Revisa que hayas ejecutado el INSERT inicial en MySQL.</p>
                """

            return f"""
            <h1>Conexión MySQL OK</h1>
            <h2>{centro.nome_oficial}</h2>
            <p><strong>Nombre corto:</strong> {centro.nome_curto}</p>
            <p><strong>Ubicación:</strong> {centro.cidade}, {centro.pais}</p>
            """

        except Exception as e:
            return f"""
            <h1>Error conectando con MySQL</h1>
            <p>Revisa el archivo <strong>.env</strong>, MySQL y la tabla <strong>centro</strong>.</p>
            <pre>{e}</pre>
            """, 500

    # Registro de Blueprints
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(portal_bp)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
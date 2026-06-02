"""Punto de entrada del Campus Virtual APPAM."""

from flask import Flask

from config import Config
from extensions import db, migrate
from routes.admin_routes import admin_bp
from routes.courses_routes import courses_bp
from routes.dashboard_routes import dashboard_bp
from routes.portal_routes import portal_bp
from services.data_service import calculate_course_progress, format_date_short, get_events, get_user_courses


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    register_context_processors(app)
    register_routes(app)
    register_blueprints(app)

    return app


def register_context_processors(app):
    @app.context_processor
    def inject_layout_data():
        layout_courses = get_user_courses()
        for course in layout_courses:
            course["_progreso"] = calculate_course_progress(course)

        layout_events = get_events(limit=3)
        for event in layout_events:
            event["_fecha_corta"] = format_date_short(event["fecha"])

        return {
            "layout_mis_cursos": layout_courses,
            "layout_eventos": layout_events,
        }


def register_routes(app):
    @app.route("/db-test")
    def db_test():
        from models import Centro

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


def register_blueprints(app):
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(portal_bp)


app = create_app()


if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])

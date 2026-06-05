"""
Configuración de la aplicación.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "academia-vertice-dev-key")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "mysql+pymysql://root:@127.0.0.1:3306/academia_profissional_albino_matos"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    TEMPLATES_AUTO_RELOAD = True

    # Contraseña simple para proteger el panel admin.
    # Definir en .env: ADMIN_PASSWORD=tu_contraseña
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")

        # Subida de archivos
    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "static",
        "uploads",
    )

    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB

    ALLOWED_UPLOAD_EXTENSIONS = {
        "pdf",
        "doc",
        "docx",
        "xls",
        "xlsx",
        "ppt",
        "pptx",
        "txt",
        "png",
        "jpg",
        "jpeg",
        "webp",
    }
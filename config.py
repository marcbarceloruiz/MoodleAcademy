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
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"connect_timeout": 3},
        "pool_pre_ping": True,
    }

    DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    TEMPLATES_AUTO_RELOAD = True

    # CSRF — Flask-WTF (usa SECRET_KEY como base)
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hora

    # Palavra-passe do painel admin. Definir em .env: ADMIN_PASSWORD=...
    # Pode ser texto simples (dev) ou hash werkzeug (recomendado para produção).
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")

    # Subida de archivos
    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "static",
        "uploads",
    )

    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB

    # Email — configurar via .env
    MAIL_SERVER   = os.environ.get("MAIL_SERVER",   "smtp.gmail.com")
    MAIL_PORT     = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS  = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get(
        "MAIL_DEFAULT_SENDER", "campus@academiaprofissional.pt"
    )

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
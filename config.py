"""Configuración de la aplicación."""

import os
from dotenv import load_dotenv

load_dotenv()


def _env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "academia-vertice-dev-key-2025")
    DEBUG = _env_bool("FLASK_DEBUG", default=False)
    TEMPLATES_AUTO_RELOAD = DEBUG

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "mysql+pymysql://root:@localhost:3306/academia_profissional_albino_matos",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

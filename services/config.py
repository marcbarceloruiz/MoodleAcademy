"""
Configuración de la aplicación.
Academia Profissional Prof. Albino de Matos - Escola Profissional Vértice
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "academia-vertice-dev-key-2025")
    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "mysql+pymysql://root:@localhost:3306/academia_profissional_albino_matos"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
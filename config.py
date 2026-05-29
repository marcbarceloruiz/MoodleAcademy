"""
Configuración de la aplicación.
"""

import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'academia-vertice-dev-key-2025')
    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True

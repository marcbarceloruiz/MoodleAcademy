"""
Blueprint: Portal Vertice.
Ruta: /portal
"""

from flask import Blueprint, render_template
from services.data_service import get_current_user, get_notices, format_date

portal_bp = Blueprint('portal', __name__)


PORTAL_CARDS = [
    {"titulo": "Normativa del Centro",   "icono": "📜", "cls": "pci-cyan",   "desc": "Reglamento interno, políticas de uso de la plataforma y normativa académica actualizada."},
    {"titulo": "Soporte Técnico",        "icono": "🛠", "cls": "pci-green",  "desc": "Asistencia para problemas de acceso, incidencias técnicas y consultas sobre la plataforma."},
    {"titulo": "Documentación",          "icono": "📁", "cls": "pci-orange", "desc": "Formularios, certificados, solicitudes y documentación administrativa del centro."},
    {"titulo": "Secretaría",             "icono": "🏛", "cls": "pci-red",    "desc": "Contacta con el personal de secretaría para gestiones académicas y administrativas."},
    {"titulo": "Calendario Académico",   "icono": "📅", "cls": "pci-blue",   "desc": "Fechas clave, períodos de exámenes, vacaciones y eventos institucionales 2024/25."},
    {"titulo": "Certificados y Títulos", "icono": "🏅", "cls": "pci-gray",   "desc": "Solicitud de certificados de asistencia, diplomas y títulos acreditativos del centro."},
    {"titulo": "Bolsa de Empleo",        "icono": "💼", "cls": "pci-green",  "desc": "Ofertas de empleo para alumnos y egresados de Academia Vertice."},
    {"titulo": "Material Didáctico",     "icono": "📚", "cls": "pci-cyan",   "desc": "Biblioteca virtual, recursos descargables y material complementario de todos los cursos."},
    {"titulo": "Tutorías Individuales",  "icono": "🎓", "cls": "pci-orange", "desc": "Solicita una sesión de tutoría personalizada con tu tutor/a asignado."},
]

LINKS_UTILES = [
    {"label": "Ministerio de Educación",        "url": "https://www.educacion.gob.es"},
    {"label": "BOE — Boletín Oficial",          "url": "https://www.boe.es"},
    {"label": "Servicio Público de Empleo (SEPE)", "url": "https://www.sepe.es"},
    {"label": "ANECA — Evaluación académica",   "url": "https://www.aneca.es"},
]


@portal_bp.route('/portal')
def portal():
    usuario = get_current_user()
    avisos  = get_notices()

    for a in avisos:
        a['_fecha'] = format_date(a['fecha'])

    return render_template(
        'portal.html',
        usuario=usuario,
        portal_cards=PORTAL_CARDS,
        links_utiles=LINKS_UTILES,
        avisos=avisos,
    )

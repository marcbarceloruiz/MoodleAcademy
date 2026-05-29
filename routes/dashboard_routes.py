"""
Blueprint: Dashboard / Mi plan formativo.
Ruta: /
"""

from flask import Blueprint, render_template
from services.data_service import (
    get_current_user, get_user_courses, get_events,
    get_notices, calculate_course_progress,
    format_date, format_date_short, estado_curso_badge
)

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def dashboard():
    usuario = get_current_user()
    mis_cursos = get_user_courses()
    eventos = get_events(limit=4)
    todos_eventos = get_events()
    avisos = get_notices()

    # Añadir progreso calculado a cada curso
    for curso in mis_cursos:
        curso['_progreso'] = calculate_course_progress(curso)
        curso['_badge'] = estado_curso_badge(curso['estado'])

    # Formatear fechas de eventos
    for ev in eventos:
        ev['_fecha_corta'] = format_date_short(ev['fecha'])

    return render_template(
        'dashboard.html',
        usuario=usuario,
        mis_cursos=mis_cursos,
        eventos=eventos,
        todos_eventos=todos_eventos,
        avisos=avisos,
        total_proximos=len(todos_eventos),
        format_date=format_date,
        format_date_short=format_date_short,
    )

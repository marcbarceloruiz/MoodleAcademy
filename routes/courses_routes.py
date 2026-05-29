"""
Blueprint: Mis cursos y detalle de curso.
Rutas: /cursos  /cursos/<id>
"""

from flask import Blueprint, render_template, request
from services.data_service import (
    get_current_user, get_courses, get_course_by_id,
    calculate_course_progress, format_date,
    estado_curso_badge, badge_estado, tipo_icono, tipo_css_class
)

courses_bp = Blueprint('courses', __name__)


@courses_bp.route('/cursos')
def courses():
    usuario = get_current_user()
    categoria = request.args.get('categoria', '')
    estado    = request.args.get('estado', '')
    query     = request.args.get('q', '')

    cursos = get_courses(
        categoria=categoria or None,
        estado=estado or None,
        query=query or None,
    )

    for c in cursos:
        c['_progreso'] = calculate_course_progress(c)
        c['_badge']    = estado_curso_badge(c['estado'])
        c['_matriculado'] = c['id'] in usuario['matriculas']
        c['_inicio']   = format_date(c['inicio'])
        c['_fin']      = format_date(c['fin'])

    filtro_activo = categoria or estado or ('todos' if not query else '')

    return render_template(
        'courses.html',
        usuario=usuario,
        cursos=cursos,
        filtro_activo=filtro_activo,
        query=query,
        total=len(cursos),
    )


@courses_bp.route('/cursos/<int:course_id>')
def course_detail(course_id):
    usuario = get_current_user()
    curso = get_course_by_id(course_id)
    if not curso:
        return render_template('404.html', usuario=usuario), 404

    progreso = calculate_course_progress(curso)
    badge    = estado_curso_badge(curso['estado'])

    # Enriquecer actividades con iconos y clases CSS
    for modulo in curso.get('modulos', []):
        for act in modulo.get('actividades', []):
            act['_icono']     = tipo_icono(act['tipo'])
            act['_css_class'] = tipo_css_class(act['tipo'])
            act['_badge']     = badge_estado(act['estado'])

    return render_template(
        'course_detail.html',
        usuario=usuario,
        curso=curso,
        progreso=progreso,
        badge=badge,
        inicio=format_date(curso['inicio']),
        fin=format_date(curso['fin']),
    )

"""
Blueprint: Mis cursos, detalle de curso y ciclos formativos.
Rutas: /cursos  /cursos/<id>  /ciclos  /ciclos/<id>
"""

from flask import Blueprint, render_template, request
from services.data_service import (
    get_current_user, get_courses, get_course_by_id,
    calculate_course_progress, format_date,
    estado_curso_badge, badge_estado, tipo_icono, tipo_css_class,
    get_ciclos_formativos, get_ciclo_by_id,
)

courses_bp = Blueprint('courses', __name__)


@courses_bp.route('/cursos')
def courses():
    usuario = get_current_user()
    categoria = request.args.get('categoria', '')
    estado = request.args.get('estado', '')
    query = request.args.get('q', '')

    cursos = get_courses(
        categoria=categoria or None,
        estado=estado or None,
        query=query or None,
    )

    for c in cursos:
        c['_progreso'] = calculate_course_progress(c)
        c['_badge'] = estado_curso_badge(c['estado'])
        c['_matriculado'] = c['id'] in usuario['matriculas']
        c['_inicio'] = format_date(c['inicio'])
        c['_fin'] = format_date(c['fin'])

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
    badge = estado_curso_badge(curso['estado'])

    for modulo in curso.get('modulos', []):
        for act in modulo.get('actividades', []):
            act['_icono'] = tipo_icono(act['tipo'])
            act['_css_class'] = tipo_css_class(act['tipo'])
            act['_badge'] = badge_estado(act['estado'])

    return render_template(
        'course_detail.html',
        usuario=usuario,
        curso=curso,
        progreso=progreso,
        badge=badge,
        inicio=format_date(curso['inicio']),
        fin=format_date(curso['fin']),
    )


@courses_bp.route('/ciclos')
def ciclos():
    """Listado de ciclos formativos de APPAM desde MySQL."""
    usuario = get_current_user()
    area = request.args.get('area', '')
    ciclos = get_ciclos_formativos(area=area or None)

    area_meta = {
        'social': ('🤝', 'Animação / Social'),
        'industrial': ('⚙', 'Industrial'),
        'madeira': ('🪵', 'Madeira / Mobiliário'),
        'design': ('🎨', 'Design'),
        'informatica': ('💻', 'Informática / Redes'),
        'efa': ('👨‍🎓', 'Cursos EFA'),
    }

    for c in ciclos:
        icono, label = area_meta.get(c.get('area'), ('📚', 'General'))
        c['_icono'] = icono
        c['_area_label'] = label

    return render_template(
        'ciclos.html',
        usuario=usuario,
        ciclos=ciclos,
        area_activa=area,
    )


@courses_bp.route('/ciclos/<int:ciclo_id>')
def ciclo_detail(ciclo_id):
    """Detalle de ciclo formativo con años y disciplinas."""
    usuario = get_current_user()
    ciclo = get_ciclo_by_id(ciclo_id)
    if not ciclo:
        return render_template('404.html', usuario=usuario), 404

    tipo_iconos = {
        'disciplina': '📘',
        'fct': '🏢',
        'pap': '🎓',
    }
    for ano in ciclo.get('anos', []):
        for disc in ano.get('disciplinas', []):
            disc['_icono'] = tipo_iconos.get(disc.get('tipo', 'disciplina'), '📘')

    return render_template(
        'ciclo_detail.html',
        usuario=usuario,
        ciclo=ciclo,
    )

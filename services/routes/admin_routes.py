"""
Blueprint: Administración.
Ruta: /admin
"""

from flask import Blueprint, render_template, request
from services.data_service import (
    get_current_user, get_admin_stats, get_students,
    get_teachers, get_courses, get_enrollments,
    calculate_course_progress, format_date,
    estado_curso_badge, get_student_by_id, get_course_by_id
)
from data.mock_data import ALUMNOS

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin')
def admin():
    usuario  = get_current_user()
    stats    = get_admin_stats()
    tab      = request.args.get('tab', 'alumnos')
    q        = request.args.get('q', '')
    estado_f = request.args.get('estado', '')

    alumnos     = get_students(query=q or None, estado=estado_f or None)
    profesores  = get_teachers()
    cursos      = get_courses()
    matriculas  = get_enrollments()

    # Enriquecer alumnos
    for a in alumnos:
        a['_ultima'] = format_date(a['ultimaConexion'])

    # Enriquecer cursos
    for c in cursos:
        c['_badge']   = estado_curso_badge(c['estado'])
        c['_alumnos'] = len([al for al in ALUMNOS if c['id'] in al['cursos']])

    return render_template(
        'admin.html',
        usuario=usuario,
        stats=stats,
        tab=tab,
        alumnos=alumnos,
        profesores=profesores,
        cursos=cursos,
        matriculas=matriculas[:15],
        q=q,
        estado_f=estado_f,
        calculate_course_progress=calculate_course_progress,
        get_course_by_id=get_course_by_id,
    )

"""
Blueprint: Mis cursos, detalle de curso y ciclos formativos.
Rutas: /cursos  /cursos/<id>  /ciclos  /ciclos/<id>
"""

from flask import Blueprint, render_template, request

from services.data_service import (
    get_current_user,
    get_courses,
    get_course_by_id,
    calculate_course_progress,
    format_date,
    estado_curso_badge,
    badge_estado,
    tipo_icono,
    tipo_css_class,
    get_ciclos_formativos,
    get_ciclo_by_id,
    get_disciplina_by_id,
)

courses_bp = Blueprint("courses", __name__)


@courses_bp.route("/cursos")
def courses():
    usuario = get_current_user()
    categoria = request.args.get("categoria", "")
    estado = request.args.get("estado", "")
    query = request.args.get("q", "")

    cursos = get_courses(
        categoria=categoria or None,
        estado=estado or None,
        query=query or None,
    )

    matriculas_usuario = usuario.get("matriculas", [])

    for curso in cursos:
        curso["_progreso"] = calculate_course_progress(curso)
        curso["_badge"] = estado_curso_badge(curso.get("estado", "en-progreso"))
        curso["_matriculado"] = curso.get("id") in matriculas_usuario

        inicio = curso.get("inicio")
        fin = curso.get("fin")

        curso["_inicio"] = format_date(inicio) if inicio else "Sin fecha"
        curso["_fin"] = format_date(fin) if fin else "Sin fecha"

    filtro_activo = categoria or estado or ("todos" if not query else "")

    return render_template(
        "courses.html",
        usuario=usuario,
        cursos=cursos,
        filtro_activo=filtro_activo,
        query=query,
        total=len(cursos),
    )


@courses_bp.route("/cursos/<int:course_id>")
def course_detail(course_id):
    usuario = get_current_user()
    curso = get_course_by_id(course_id)

    if not curso:
        return render_template("404.html", usuario=usuario), 404

    progreso = calculate_course_progress(curso)
    badge = estado_curso_badge(curso.get("estado", "en-progreso"))

    for modulo in curso.get("modulos", []):
        for actividad in modulo.get("actividades", []):
            actividad["_icono"] = tipo_icono(actividad.get("tipo"))
            actividad["_css_class"] = tipo_css_class(actividad.get("tipo"))
            actividad["_badge"] = badge_estado(actividad.get("estado"))

    inicio = curso.get("inicio")
    fin = curso.get("fin")

    return render_template(
        "course_detail.html",
        usuario=usuario,
        curso=curso,
        progreso=progreso,
        badge=badge,
        inicio=format_date(inicio) if inicio else "Sin fecha",
        fin=format_date(fin) if fin else "Sin fecha",
    )


@courses_bp.route("/ciclos")
def ciclos():
    """
    Listado de ciclos formativos de APPAM desde MySQL.
    """
    usuario = get_current_user()
    area = request.args.get("area", "")

    ciclos_lista = get_ciclos_formativos(area=area or None)

    area_meta = {
        "social": ("🤝", "Animação / Social"),
        "industrial": ("⚙", "Industrial"),
        "madeira": ("🪵", "Madeira / Mobiliário"),
        "design": ("🎨", "Design"),
        "informatica": ("💻", "Informática / Redes"),
        "efa": ("👨‍🎓", "Cursos EFA"),
    }

    for ciclo in ciclos_lista:
        icono, label = area_meta.get(ciclo.get("area"), ("📚", "General"))
        ciclo["_icono"] = icono
        ciclo["_area_label"] = label

    return render_template(
        "ciclos.html",
        usuario=usuario,
        ciclos=ciclos_lista,
        area_activa=area,
    )


@courses_bp.route("/ciclos/<int:ciclo_id>")
def ciclo_detail(ciclo_id):
    """
    Detalle de ciclo formativo con años, disciplinas, FCT y PAP.
    """
    usuario = get_current_user()
    ciclo = get_ciclo_by_id(ciclo_id)

    if not ciclo:
        return render_template("404.html", usuario=usuario), 404

    tipo_iconos = {
        "disciplina": "📘",
        "fct": "🏢",
        "pap": "🎓",
    }

    for ano in ciclo.get("anos", []):
        for disciplina in ano.get("disciplinas", []):
            disciplina["_icono"] = tipo_iconos.get(
                disciplina.get("tipo", "disciplina"),
                "📘",
            )

    return render_template(
        "ciclo_detail.html",
        usuario=usuario,
        ciclo=ciclo,
    )
@courses_bp.route("/disciplinas/<int:disciplina_id>")
def disciplina_detail(disciplina_id):
    """
    Detalle tipo Moodle de una disciplina/asignatura.
    """
    usuario = get_current_user()
    disciplina = get_disciplina_by_id(disciplina_id)

    if not disciplina:
        return render_template("404.html", usuario=usuario), 404

    return render_template(
        "disciplina_detail.html",
        usuario=usuario,
        disciplina=disciplina,
    )
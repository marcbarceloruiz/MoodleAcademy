"""
Blueprint: Mis cursos, detalle de curso y ciclos formativos.
Rutas: /cursos  /cursos/<id>  /ciclos  /ciclos/<id>
"""

from flask import Blueprint, render_template, request, session

from sqlalchemy import text
from extensions import db

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
    from sqlalchemy import bindparam

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
                disciplina.get("tipo", "disciplina"), "📘",
            )
            disciplina["_progresso_pct"]   = 0
            disciplina["_progresso_done"]  = 0
            disciplina["_progresso_total"] = 0

    # Progresso real do aluno por disciplina
    usuario_id = session.get("usuario_id")
    if usuario_id:
        disc_ids = [
            d["id"]
            for a in ciclo.get("anos", [])
            for d in a.get("disciplinas", [])
            if d.get("id")
        ]
        if disc_ids:
            try:
                totals = {
                    r["disciplina_id"]: r["total"]
                    for r in db.session.execute(
                        text("""
                            SELECT s.disciplina_id, COUNT(r.id) AS total
                            FROM recursos_disciplina r
                            JOIN secciones_disciplina s ON s.id = r.seccion_id
                            WHERE r.visible = 1
                              AND s.disciplina_id IN :ids
                            GROUP BY s.disciplina_id
                        """).bindparams(bindparam("ids", expanding=True)),
                        {"ids": disc_ids},
                    ).mappings().all()
                }
                dones = {
                    r["disciplina_id"]: r["done"]
                    for r in db.session.execute(
                        text("""
                            SELECT s.disciplina_id, COUNT(rc.id) AS done
                            FROM recurso_conclusao rc
                            JOIN recursos_disciplina r ON r.id = rc.recurso_id
                            JOIN secciones_disciplina s ON s.id = r.seccion_id
                            WHERE rc.usuario_id = :uid
                              AND s.disciplina_id IN :ids
                            GROUP BY s.disciplina_id
                        """).bindparams(bindparam("ids", expanding=True)),
                        {"uid": usuario_id, "ids": disc_ids},
                    ).mappings().all()
                }
                for ano in ciclo.get("anos", []):
                    for disc in ano.get("disciplinas", []):
                        total = totals.get(disc["id"], 0)
                        done  = dones.get(disc["id"], 0)
                        disc["_progresso_total"] = total
                        disc["_progresso_done"]  = done
                        disc["_progresso_pct"]   = int(done / total * 100) if total else 0
            except Exception:
                pass

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

    usuario_id = session.get("usuario_id")

    # IDs de recursos ya completados por este usuario
    concluidos = set()
    # IDs de recursos con entrega ya realizada por este usuario
    entregues = {}

    if usuario_id:
        try:
            rows = db.session.execute(
                text("SELECT recurso_id FROM recurso_conclusao WHERE usuario_id = :u"),
                {"u": usuario_id},
            ).mappings().all()
            concluidos = {r["recurso_id"] for r in rows}
        except Exception:
            pass

        try:
            rows = db.session.execute(
                text("""
                    SELECT recurso_id, data_entrega, nota, estado
                    FROM entregas
                    WHERE usuario_id = :u AND recurso_id IS NOT NULL
                    ORDER BY data_entrega DESC
                """),
                {"u": usuario_id},
            ).mappings().all()
            for r in rows:
                if r["recurso_id"] not in entregues:
                    entregues[r["recurso_id"]] = {
                        "dt":     r["data_entrega"],
                        "nota":   r["nota"],
                        "estado": r["estado"],
                    }
        except Exception:
            pass

    # Progresso por secção
    for seccion in disciplina.get("secciones", []):
        recursos = seccion.get("recursos", [])
        total = len(recursos)
        done = sum(1 for r in recursos if r.get("id") in concluidos)
        seccion["_progresso_total"] = total
        seccion["_progresso_done"] = done
        seccion["_progresso_pct"] = int(done / total * 100) if total else 0

    from datetime import datetime
    return render_template(
        "disciplina_detail.html",
        usuario=usuario,
        disciplina=disciplina,
        concluidos=concluidos,
        entregues=entregues,
        now=datetime.now(),
    )
"""
Capa de servicio de datos.
Todas las vistas deben usar estas funciones en lugar de
acceder directamente a mock_data. Así, en el futuro,
basta con cambiar estas funciones para conectar una BD real.
"""

from data.mock_data import (
    USUARIO, CURSOS, ALUMNOS, PROFESORES, EVENTOS, AVISOS, ESTADISTICAS
)
from datetime import date


# ──────────────────────────────────────────────
# USUARIO
# ──────────────────────────────────────────────

def get_current_user():
    return USUARIO


# ──────────────────────────────────────────────
# CURSOS
# ──────────────────────────────────────────────

def get_courses(categoria=None, estado=None, query=None):
    cursos = CURSOS[:]
    if categoria:
        cursos = [c for c in cursos if c["categoria"] == categoria]
    if estado:
        cursos = [c for c in cursos if c["estado"] == estado]
    if query:
        q = query.lower()
        cursos = [c for c in cursos if
                  q in c["titulo"].lower() or
                  q in c["tutor"].lower() or
                  q in c["categoria"].lower()]
    return cursos


def get_course_by_id(course_id):
    return next((c for c in CURSOS if c["id"] == course_id), None)


def get_user_courses():
    ids = USUARIO["matriculas"]
    return [c for c in CURSOS if c["id"] in ids]


def calculate_course_progress(course):
    """
    Calcula el progreso de un curso contando actividades no bloqueadas
    marcadas como completadas.
    """
    total = 0
    completadas = 0
    for modulo in course.get("modulos", []):
        for act in modulo.get("actividades", []):
            if act["estado"] != "bloqueado":
                total += 1
                if act["estado"] == "completado":
                    completadas += 1
    if total == 0:
        return course.get("progreso", 0)
    return round((completadas / total) * 100)


# ──────────────────────────────────────────────
# ALUMNOS Y PROFESORES
# ──────────────────────────────────────────────

def get_students(query=None, estado=None):
    alumnos = ALUMNOS[:]
    if query:
        q = query.lower()
        alumnos = [a for a in alumnos if
                   q in a["nombre"].lower() or q in a["email"].lower()]
    if estado:
        alumnos = [a for a in alumnos if a["estado"] == estado]
    return alumnos


def get_student_by_id(student_id):
    return next((a for a in ALUMNOS if a["id"] == student_id), None)


def get_teachers():
    return PROFESORES


# ──────────────────────────────────────────────
# EVENTOS Y AVISOS
# ──────────────────────────────────────────────

def get_events(limit=None):
    """
    Devuelve eventos próximos. Para que la demo no quede vacía si las fechas
    simuladas son antiguas, si no encuentra eventos futuros devuelve todos.
    """
    today = date.today().isoformat()
    proximos = sorted(
        [e for e in EVENTOS if e["fecha"] >= today],
        key=lambda e: e["fecha"]
    )

    if not proximos:
        proximos = sorted(EVENTOS, key=lambda e: e["fecha"])

    if limit:
        return proximos[:limit]
    return proximos


def get_all_events():
    return sorted(EVENTOS, key=lambda e: e["fecha"])


def get_notices():
    return AVISOS


# ──────────────────────────────────────────────
# ADMINISTRACIÓN
# ──────────────────────────────────────────────

def get_admin_stats():
    return ESTADISTICAS


def get_enrollments():
    """
    Devuelve lista plana de matrículas: alumno + curso + tutor.
    """
    enrollments = []
    for alumno in ALUMNOS:
        for curso_id in alumno["cursos"]:
            curso = get_course_by_id(curso_id)
            if curso:
                enrollments.append({
                    "alumno": alumno["nombre"],
                    "alumno_estado": alumno["estado"],
                    "curso": curso["titulo"],
                    "tutor": curso["tutor"],
                })
    return enrollments


# ──────────────────────────────────────────────
# UTILIDADES
# ──────────────────────────────────────────────

def format_date(iso_str):
    from datetime import datetime
    try:
        d = datetime.strptime(iso_str, "%Y-%m-%d")
        meses = ["enero","febrero","marzo","abril","mayo","junio",
                 "julio","agosto","septiembre","octubre","noviembre","diciembre"]
        return f"{d.day} de {meses[d.month - 1]} de {d.year}"
    except Exception:
        return iso_str


def format_date_short(iso_str):
    from datetime import datetime
    try:
        d = datetime.strptime(iso_str, "%Y-%m-%d")
        meses = ["ene","feb","mar","abr","may","jun",
                 "jul","ago","sep","oct","nov","dic"]
        return f"{d.day:02d} {meses[d.month - 1].upper()}"
    except Exception:
        return iso_str


def tipo_icono(tipo):
    return {"video": "▶", "pdf": "📄", "tarea": "✏", "test": "✅", "foro": "💬"}.get(tipo, "◈")


def tipo_css_class(tipo):
    return {
        "video": "ai-video", "pdf": "ai-pdf", "tarea": "ai-tarea",
        "test": "ai-test", "foro": "ai-foro"
    }.get(tipo, "ai-video")


def estado_curso_badge(estado):
    return {
        "en-progreso":  ("status-en-progreso", "En progreso"),
        "completado":   ("status-completado",   "Completado"),
        "no-comenzado": ("status-no-comenzado", "No comenzado"),
    }.get(estado, ("status-no-comenzado", estado))


def badge_estado(estado):
    return {
        "completado":   ("ab-completado",   "Completado"),
        "pendiente":    ("ab-pendiente",    "Pendiente"),
        "bloqueado":    ("ab-bloqueado",    "Bloqueado"),
        "no-comenzado": ("ab-no-comenzado", "No comenzado"),
        "abierto":      ("ab-abierto",      "Abierto"),
    }.get(estado, ("ab-no-comenzado", estado))

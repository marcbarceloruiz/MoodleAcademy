"""Servicio único de datos para las vistas.

La aplicación todavía usa datos simulados para gran parte del campus. Esta capa
permite cambiar a MySQL progresivamente sin tocar templates ni rutas.
"""

from datetime import date, datetime

from data.ciclos_data import CICLOS_FALLBACK, DEFAULT_CICLO_ANOS
from data.mock_data import ALUMNOS, AVISOS, CURSOS, ESTADISTICAS, EVENTOS, PROFESORES, USUARIO

CENTRO_FALLBACK = {
    "nome_oficial": "Academia Profissional Prof. Albino de Matos - Escola Profissional Vértice",
    "nome_curto": "Escola Profissional Vértice",
    "cidade": "Paços de Ferreira",
    "pais": "Portugal",
    "nombre_oficial": "Academia Profissional Prof. Albino de Matos - Escola Profissional Vértice",
    "nombre_corto": "Escola Profissional Vértice",
    "ciudad": "Paços de Ferreira",
}

MONTHS_ES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]
MONTHS_ES_SHORT = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]

ACTIVITY_ICONS = {"video": "▶", "pdf": "📄", "tarea": "✏", "test": "✅", "foro": "💬"}
ACTIVITY_CLASSES = {
    "video": "ai-video",
    "pdf": "ai-pdf",
    "tarea": "ai-tarea",
    "test": "ai-test",
    "foro": "ai-foro",
}
COURSE_BADGES = {
    "en-progreso": ("status-en-progreso", "En progreso"),
    "completado": ("status-completado", "Completado"),
    "no-comenzado": ("status-no-comenzado", "No comenzado"),
}
ACTIVITY_BADGES = {
    "completado": ("ab-completado", "Completado"),
    "pendiente": ("ab-pendiente", "Pendiente"),
    "bloqueado": ("ab-bloqueado", "Bloqueado"),
    "no-comenzado": ("ab-no-comenzado", "No comenzado"),
    "abierto": ("ab-abierto", "Abierto"),
}


def get_current_user():
    return USUARIO


def get_courses(categoria=None, estado=None, query=None):
    cursos = list(CURSOS)
    if categoria:
        cursos = [c for c in cursos if c["categoria"] == categoria]
    if estado:
        cursos = [c for c in cursos if c["estado"] == estado]
    if query:
        q = query.lower()
        cursos = [
            c for c in cursos
            if q in c["titulo"].lower()
            or q in c["tutor"].lower()
            or q in c["categoria"].lower()
        ]
    return cursos


def get_course_by_id(course_id):
    return next((c for c in CURSOS if c["id"] == course_id), None)


def get_user_courses():
    return [c for c in CURSOS if c["id"] in USUARIO["matriculas"]]


def calculate_course_progress(course):
    total = 0
    completed = 0
    for module in course.get("modulos", []):
        for activity in module.get("actividades", []):
            if activity["estado"] != "bloqueado":
                total += 1
                completed += activity["estado"] == "completado"
    return round((completed / total) * 100) if total else course.get("progreso", 0)


def get_students(query=None, estado=None):
    alumnos = list(ALUMNOS)
    if query:
        q = query.lower()
        alumnos = [a for a in alumnos if q in a["nombre"].lower() or q in a["email"].lower()]
    if estado:
        alumnos = [a for a in alumnos if a["estado"] == estado]
    return alumnos


def get_student_by_id(student_id):
    return next((a for a in ALUMNOS if a["id"] == student_id), None)


def get_teachers():
    return PROFESORES


def get_events(limit=None):
    today = date.today().isoformat()
    events = sorted([e for e in EVENTOS if e["fecha"] >= today], key=lambda e: e["fecha"])
    if not events:
        events = sorted(EVENTOS, key=lambda e: e["fecha"])
    return events[:limit] if limit else events


def get_all_events():
    return sorted(EVENTOS, key=lambda e: e["fecha"])


def get_notices():
    return AVISOS


def get_admin_stats():
    return ESTADISTICAS


def get_enrollments():
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


def format_date(iso_str):
    try:
        d = datetime.strptime(iso_str, "%Y-%m-%d")
        return f"{d.day} de {MONTHS_ES[d.month - 1]} de {d.year}"
    except Exception:
        return iso_str


def format_date_short(iso_str):
    try:
        d = datetime.strptime(iso_str, "%Y-%m-%d")
        return f"{d.day:02d} {MONTHS_ES_SHORT[d.month - 1].upper()}"
    except Exception:
        return iso_str


def tipo_icono(tipo):
    return ACTIVITY_ICONS.get(tipo, "◈")


def tipo_css_class(tipo):
    return ACTIVITY_CLASSES.get(tipo, "ai-video")


def estado_curso_badge(estado):
    return COURSE_BADGES.get(estado, ("status-no-comenzado", estado))


def badge_estado(estado):
    return ACTIVITY_BADGES.get(estado, ("ab-no-comenzado", estado))


def get_centro():
    """Centro desde MySQL, con fallback seguro para demo/local."""
    try:
        from models.centro import Centro
        centro = Centro.query.first()
        if centro:
            return {
                "nome_oficial": centro.nome_oficial,
                "nome_curto": centro.nome_curto,
                "cidade": centro.cidade,
                "pais": centro.pais,
                "nombre_oficial": centro.nome_oficial,
                "nombre_corto": centro.nome_curto,
                "ciudad": centro.cidade,
            }
    except Exception:
        pass
    return dict(CENTRO_FALLBACK)


def get_areas_moodle(tipo=None):
    try:
        from models.area_moodle import AreaMoodle
        query = AreaMoodle.query.filter_by(visible=True)
        if tipo:
            query = query.filter_by(tipo=tipo)
        return [_area_to_dict(area) for area in query.order_by(AreaMoodle.orden).all()]
    except Exception:
        return []


def get_area_by_slug(slug):
    try:
        from models.area_moodle import AreaMoodle
        area = AreaMoodle.query.filter_by(slug=slug, visible=True).first()
        return _area_to_dict(area) if area else None
    except Exception:
        return None


def get_documentos_by_area(area_slug):
    try:
        from models.area_moodle import AreaMoodle, DocumentoInstitucional
        area = AreaMoodle.query.filter_by(slug=area_slug).first()
        if not area:
            return []
        docs = DocumentoInstitucional.query.filter_by(area_id=area.id, visible=True).order_by(DocumentoInstitucional.orden).all()
        return [
            {"id": d.id, "titulo": d.titulo, "descripcion": d.descripcion, "tipo": d.tipo, "url": d.url}
            for d in docs
        ]
    except Exception:
        return []


def get_ciclos_formativos(area=None):
    try:
        from models.ciclo_formativo import CicloFormativo
        query = CicloFormativo.query.filter_by(activo=True)
        if area:
            query = query.filter_by(area=area)
        ciclos = [_ciclo_to_dict(c) for c in query.order_by(CicloFormativo.orden, CicloFormativo.id).all()]
        if ciclos:
            return ciclos
    except Exception:
        pass
    return [c for c in CICLOS_FALLBACK if c["area"] == area] if area else list(CICLOS_FALLBACK)


def get_ciclo_by_id(ciclo_id):
    try:
        from models.ciclo_formativo import CicloFormativo
        ciclo = CicloFormativo.query.get(ciclo_id)
        if ciclo:
            return _ciclo_to_dict_full(ciclo)
    except Exception:
        pass

    ciclo = next((c for c in CICLOS_FALLBACK if c["id"] == ciclo_id), None)
    if not ciclo:
        return None
    data = dict(ciclo)
    data["anos"] = DEFAULT_CICLO_ANOS
    return data


def _area_to_dict(area):
    return {
        "id": area.id,
        "slug": area.slug,
        "nombre": area.nombre,
        "descripcion": area.descripcion,
        "icono": area.icono,
        "tipo": area.tipo,
        "orden": area.orden,
        "restringido": area.restringido,
    }


def _ciclo_to_dict(ciclo):
    return {
        "id": ciclo.id,
        "codigo": ciclo.codigo,
        "nombre": ciclo.nombre,
        "area": ciclo.area,
        "nivel": ciclo.nivel,
        "duracion": ciclo.duracion,
        "descripcion": ciclo.descripcion,
    }


def _ciclo_to_dict_full(ciclo):
    data = _ciclo_to_dict(ciclo)
    data["anos"] = []
    for ano in ciclo.anos:
        data["anos"].append({
            "id": ano.id,
            "numero": ano.numero,
            "ano_escolar": ano.ano_escolar,
            "descripcion": ano.descripcion,
            "disciplinas": [
                {
                    "id": d.id,
                    "codigo": d.codigo,
                    "nombre": d.nombre,
                    "tipo": d.tipo,
                    "horas": d.horas,
                    "descripcion": d.descripcion,
                }
                for d in ano.disciplinas
            ],
        })
    return data

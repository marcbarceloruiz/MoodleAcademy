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


# ──────────────────────────────────────────────
# BD APPAM / ESTRUCTURA MOODLE REAL
# ──────────────────────────────────────────────

def get_centro():
    """Devuelve datos del centro desde MySQL, con fallback seguro."""
    try:
        from models.centro import Centro
        c = Centro.query.first()
        if c:
            return {
                "nome_oficial": c.nome_oficial,
                "nome_curto": c.nome_curto,
                "cidade": c.cidade,
                "pais": c.pais,
                "nombre_oficial": c.nome_oficial,
                "nombre_corto": c.nome_curto,
                "ciudad": c.cidade,
            }
    except Exception:
        pass

    return {
        "nome_oficial": "Academia Profissional Prof. Albino de Matos - Escola Profissional Vértice",
        "nome_curto": "Escola Profissional Vértice",
        "cidade": "Paços de Ferreira",
        "pais": "Portugal",
        "nombre_oficial": "Academia Profissional Prof. Albino de Matos - Escola Profissional Vértice",
        "nombre_corto": "Escola Profissional Vértice",
        "ciudad": "Paços de Ferreira",
    }


def get_areas_moodle(tipo=None):
    """Áreas institucionales del campus desde MySQL, con fallback vacío."""
    try:
        from models.area_moodle import AreaMoodle
        q = AreaMoodle.query.filter_by(visible=True)
        if tipo:
            q = q.filter_by(tipo=tipo)
        return [_area_to_dict(a) for a in q.order_by(AreaMoodle.orden).all()]
    except Exception:
        return []


def get_area_by_slug(slug):
    try:
        from models.area_moodle import AreaMoodle
        a = AreaMoodle.query.filter_by(slug=slug, visible=True).first()
        return _area_to_dict(a) if a else None
    except Exception:
        return None


def get_documentos_by_area(area_slug):
    try:
        from models.area_moodle import AreaMoodle, DocumentoInstitucional
        area = AreaMoodle.query.filter_by(slug=area_slug).first()
        if not area:
            return []
        docs = DocumentoInstitucional.query.filter_by(
            area_id=area.id,
            visible=True,
        ).order_by(DocumentoInstitucional.orden).all()
        return [
            {
                "id": d.id,
                "titulo": d.titulo,
                "descripcion": d.descripcion,
                "tipo": d.tipo,
                "url": d.url,
            }
            for d in docs
        ]
    except Exception:
        return []


def _area_to_dict(a):
    return {
        "id": a.id,
        "slug": a.slug,
        "nombre": a.nombre,
        "descripcion": a.descripcion,
        "icono": a.icono,
        "tipo": a.tipo,
        "orden": a.orden,
        "restringido": a.restringido,
    }


def _ciclos_fallback():
    return [
        {"id": 1, "codigo": "CP-AMC", "nombre": "Curso Profissional - Animação e Mediação Comunitária", "area": "social", "nivel": "Nível 4", "duracion": "3 anos", "descripcion": "Curso profissional orientado para intervenção comunitária, animação sociocultural e mediação."},
        {"id": 2, "codigo": "CP-CIND", "nombre": "Curso Profissional - Construção Industrial", "area": "industrial", "nivel": "Nível 4", "duracion": "3 anos", "descripcion": "Formação na área da construção industrial, processos técnicos e segurança."},
        {"id": 3, "codigo": "CP-DPMM", "nombre": "Curso Profissional - Desenho de Produto em Madeira e Mobiliário", "area": "madeira", "nivel": "Nível 4", "duracion": "3 anos", "descripcion": "Desenho de produto, mobiliário, materiais e soluções ligadas à madeira."},
        {"id": 4, "codigo": "CP-DIE", "nombre": "Curso Profissional - Design de Interiores e Exteriores", "area": "design", "nivel": "Nível 4", "duracion": "3 anos", "descripcion": "Projeto de espaços interiores e exteriores, representação visual e materiais."},
        {"id": 5, "codigo": "CP-DEQ", "nombre": "Curso Profissional - Design de Equipamentos", "area": "design", "nivel": "Nível 4", "duracion": "3 anos", "descripcion": "Design de equipamentos, ergonomia, materiais e desenvolvimento de produto."},
        {"id": 6, "codigo": "CP-IE", "nombre": "Curso Profissional - Instalações Elétricas", "area": "industrial", "nivel": "Nível 4", "duracion": "3 anos", "descripcion": "Eletricidade, instalações, manutenção, segurança e sistemas elétricos."},
        {"id": 7, "codigo": "CP-PMCNC", "nombre": "Curso Profissional - Programação e Maquinação CNC", "area": "industrial", "nivel": "Nível 4", "duracion": "3 anos", "descripcion": "Programação, maquinação CNC, CAD/CAM e controlo de produção."},
        {"id": 8, "codigo": "CP-SCR", "nombre": "Curso Profissional - Sistemas de Computação e Redes", "area": "informatica", "nivel": "Nível 4", "duracion": "3 anos", "descripcion": "Redes, sistemas, hardware, administração e suporte informático."},
        {"id": 9, "codigo": "EFA-AG", "nombre": "Curso EFA - Agente em Geriatria", "area": "efa", "nivel": "EFA", "duracion": "Adultos", "descripcion": "Educação e Formação de Adultos na área de geriatria."},
        {"id": 10, "codigo": "EFA-CSD", "nombre": "Curso EFA - Comunicação e Serviço Digital", "area": "efa", "nivel": "EFA", "duracion": "Adultos", "descripcion": "Comunicação digital, ferramentas tecnológicas e serviços digitais."},
        {"id": 11, "codigo": "EFA-IIGR", "nombre": "Curso EFA - Informática - Instalação e Gestão de Redes", "area": "efa", "nivel": "EFA", "duracion": "Adultos", "descripcion": "Instalação, manutenção e gestão de redes."},
        {"id": 12, "codigo": "EFA-DMCM", "nombre": "Curso EFA - Desenho de Mobiliário e Construções em Madeira", "area": "efa", "nivel": "EFA", "duracion": "Adultos", "descripcion": "Desenho de mobiliário, construção em madeira e processos técnicos."},
    ]


def get_ciclos_formativos(area=None):
    """Ciclos desde MySQL. Si no hay seed, devuelve fallback real basado en la demo."""
    try:
        from models.ciclo_formativo import CicloFormativo
        q = CicloFormativo.query.filter_by(activo=True)
        if area:
            q = q.filter_by(area=area)
        result = [_ciclo_to_dict(c) for c in q.order_by(CicloFormativo.orden, CicloFormativo.id).all()]
        if result:
            return result
    except Exception:
        pass
    data = _ciclos_fallback()
    return [c for c in data if c["area"] == area] if area else data


def get_ciclo_by_id(ciclo_id):
    try:
        from models.ciclo_formativo import CicloFormativo
        c = CicloFormativo.query.get(ciclo_id)
        if c:
            return _ciclo_to_dict_full(c)
    except Exception:
        pass
    ciclo = next((c for c in _ciclos_fallback() if c["id"] == ciclo_id), None)
    if not ciclo:
        return None
    ciclo = dict(ciclo)
    ciclo["anos"] = [
        {"numero": 1, "ano_escolar": "10º", "disciplinas": [
            {"nombre": "Português", "tipo": "disciplina"}, {"nombre": "Inglês", "tipo": "disciplina"}, {"nombre": "Área de Integração", "tipo": "disciplina"}, {"nombre": "Formação Técnica I", "tipo": "disciplina"}]},
        {"numero": 2, "ano_escolar": "11º", "disciplinas": [
            {"nombre": "Português", "tipo": "disciplina"}, {"nombre": "Inglês Técnico", "tipo": "disciplina"}, {"nombre": "Formação Técnica II", "tipo": "disciplina"}, {"nombre": "Projeto Técnico", "tipo": "disciplina"}]},
        {"numero": 3, "ano_escolar": "12º", "disciplinas": [
            {"nombre": "Formação Técnica III", "tipo": "disciplina"}, {"nombre": "FCT — Formação em Contexto de Trabalho", "tipo": "fct"}, {"nombre": "PAP — Prova de Aptidão Profissional", "tipo": "pap"}]},
    ]
    return ciclo


def _ciclo_to_dict(c):
    return {
        "id": c.id,
        "codigo": c.codigo,
        "nombre": c.nombre,
        "area": c.area,
        "nivel": c.nivel,
        "duracion": c.duracion,
        "descripcion": c.descripcion,
    }


def _ciclo_to_dict_full(c):
    data = _ciclo_to_dict(c)
    data["anos"] = []
    for ano in c.anos:
        ano_data = {
            "id": ano.id,
            "numero": ano.numero,
            "ano_escolar": ano.ano_escolar,
            "descripcion": ano.descripcion,
            "disciplinas": [],
        }
        for d in ano.disciplinas:
            ano_data["disciplinas"].append({
                "id": d.id,
                "codigo": d.codigo,
                "nombre": d.nombre,
                "tipo": d.tipo,
                "horas": d.horas,
                "descripcion": d.descripcion,
            })
        data["anos"].append(ano_data)
    return data

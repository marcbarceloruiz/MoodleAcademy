"""
Capa de servicio de datos.

Las vistas deben usar estas funciones en lugar de acceder directamente
a mock_data o a la base de datos.

Ahora el servicio intenta leer primero desde MySQL.
Si algo falla o no hay datos, usa los datos mock como fallback seguro.
"""

from datetime import date, datetime

from sqlalchemy import text

from extensions import db

from data.mock_data import (
    USUARIO,
    CURSOS,
    ALUMNOS,
    PROFESORES,
    EVENTOS,
    AVISOS,
    ESTADISTICAS,
)


# ──────────────────────────────────────────────
# USUARIO
# ──────────────────────────────────────────────

def get_current_user():
    """
    Usuario actual de demo.

    De momento no hay login real, así que se mantiene el usuario mock.
    Más adelante esta función leerá del usuario autenticado.
    """
    return USUARIO


# ──────────────────────────────────────────────
# CENTRO
# ──────────────────────────────────────────────

def get_centro():
    """
    Devuelve datos del centro desde MySQL, con fallback seguro.
    """
    try:
        row = db.session.execute(
            text("""
                SELECT
                    nome_oficial,
                    nome_curto,
                    cidade,
                    pais,
                    logo_url
                FROM centro
                LIMIT 1
            """)
        ).mappings().first()

        if row:
            return {
                "nome_oficial": row["nome_oficial"],
                "nome_curto": row["nome_curto"],
                "cidade": row["cidade"],
                "pais": row["pais"],
                "logo_url": row["logo_url"],

                # Compatibilidad con nombres en español usados en algunas plantillas
                "nombre_oficial": row["nome_oficial"],
                "nombre_corto": row["nome_curto"],
                "ciudad": row["cidade"],
            }

    except Exception as e:
        print("Error cargando centro desde MySQL:", e)

    return {
        "nome_oficial": "Academia Profissional Prof. Albino de Matos - Escola Profissional Vértice",
        "nome_curto": "Escola Profissional Vértice",
        "cidade": "Paços de Ferreira",
        "pais": "Portugal",
        "logo_url": "/static/img/logo-appam.webp",

        "nombre_oficial": "Academia Profissional Prof. Albino de Matos - Escola Profissional Vértice",
        "nombre_corto": "Escola Profissional Vértice",
        "ciudad": "Paços de Ferreira",
    }


# ──────────────────────────────────────────────
# CURSOS
# ──────────────────────────────────────────────

def _curso_mysql_to_dict(row):
    """
    Convierte una fila de MySQL en el formato que esperan las plantillas.
    """
    progreso = row.get("progreso", 0) or 0
    tipo = row.get("tipo") or "profissional"

    return {
        "id": row["id"],
        "titulo": row["titulo"],
        "codigo": row.get("codigo") or "",
        "descripcion": row.get("descripcion") or "",
        "descricao": row.get("descripcion") or "",
        "categoria": tipo,
        "tipo": tipo,
        "estado": row.get("estado") or "en-progreso",
        "progreso": progreso,
        "_progreso": progreso,

        # Compatibilidad con tarjetas antiguas
        "tutor": row.get("tutor") or "Prof. Albino de Matos",
        "profesor": row.get("tutor") or "Prof. Albino de Matos",
        "modulos": [],
    }


def get_courses(categoria=None, estado=None, query=None):
    """
    Devuelve cursos desde MySQL si es posible.
    Si no hay datos o falla MySQL, usa CURSOS mock.
    """
    try:
        sql = """
            SELECT
                c.id,
                c.titulo,
                c.codigo,
                c.descricao AS descripcion,
                c.tipo,
                c.activo,
                NULL AS progreso,
                NULL AS estado,
                'Prof. Albino de Matos' AS tutor
            FROM cursos c
            WHERE c.activo = 1
        """

        params = {}

        if categoria:
            sql += " AND c.tipo = :categoria"
            params["categoria"] = categoria

        if query:
            sql += """
                AND (
                    LOWER(c.titulo) LIKE :query
                    OR LOWER(c.codigo) LIKE :query
                    OR LOWER(c.tipo) LIKE :query
                )
            """
            params["query"] = f"%{query.lower()}%"

        sql += " ORDER BY c.id ASC"

        rows = db.session.execute(text(sql), params).mappings().all()
        cursos = [_curso_mysql_to_dict(row) for row in rows]

        if estado:
            cursos = [c for c in cursos if c["estado"] == estado]

        if cursos:
            return cursos

    except Exception as e:
        print("Error cargando cursos desde MySQL:", e)

    # Fallback mock
    cursos = CURSOS[:]

    if categoria:
        cursos = [c for c in cursos if c.get("categoria") == categoria]

    if estado:
        cursos = [c for c in cursos if c.get("estado") == estado]

    if query:
        q = query.lower()
        cursos = [
            c for c in cursos
            if q in c.get("titulo", "").lower()
            or q in c.get("tutor", "").lower()
            or q in c.get("categoria", "").lower()
        ]

    return cursos


def get_course_by_id(course_id):
    """
    Devuelve un curso por ID desde MySQL si existe.
    Si no, usa CURSOS mock.
    """
    try:
        row = db.session.execute(
            text("""
                SELECT
                    c.id,
                    c.titulo,
                    c.codigo,
                    c.descricao AS descripcion,
                    c.tipo,
                    c.activo,
                    NULL AS progreso,
                    NULL AS estado,
                    'Prof. Albino de Matos' AS tutor
                FROM cursos c
                WHERE c.id = :course_id
                LIMIT 1
            """),
            {"course_id": course_id}
        ).mappings().first()

        if row:
            return _curso_mysql_to_dict(row)

    except Exception as e:
        print("Error cargando curso por ID desde MySQL:", e)

    return next((c for c in CURSOS if c["id"] == course_id), None)


def get_user_courses(usuario_id=1):
    """
    Devuelve los cursos matriculados del usuario demo desde MySQL.

    De momento usamos usuario_id=1 hasta tener login real.
    Si falla MySQL, usa las matrículas del usuario mock.
    """
    try:
        rows = db.session.execute(
            text("""
                SELECT
                    c.id,
                    c.titulo,
                    c.codigo,
                    c.descricao AS descripcion,
                    c.tipo,
                    m.progreso,
                    m.estado,
                    'Prof. Albino de Matos' AS tutor
                FROM matriculas m
                JOIN cursos c ON c.id = m.curso_id
                WHERE m.usuario_id = :usuario_id
                  AND c.activo = 1
                ORDER BY c.id ASC
            """),
            {"usuario_id": usuario_id}
        ).mappings().all()

        cursos = [_curso_mysql_to_dict(row) for row in rows]

        if cursos:
            return cursos

    except Exception as e:
        print("Error cargando cursos del usuario desde MySQL:", e)

    # Fallback mock
    ids = USUARIO.get("matriculas", [])
    return [c for c in CURSOS if c["id"] in ids]


def calculate_course_progress(course):
    """
    Calcula o devuelve el progreso de un curso.

    Compatible con:
    - cursos MySQL: progreso / _progreso
    - cursos mock: modulos y actividades
    """
    if "_progreso" in course:
        return course.get("_progreso") or 0

    if "progreso" in course:
        return course.get("progreso") or 0

    total = 0
    completadas = 0

    for modulo in course.get("modulos", []):
        for act in modulo.get("actividades", []):
            if act.get("estado") != "bloqueado":
                total += 1
                if act.get("estado") == "completado":
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
        alumnos = [
            a for a in alumnos
            if q in a.get("nombre", "").lower()
            or q in a.get("email", "").lower()
        ]

    if estado:
        alumnos = [a for a in alumnos if a.get("estado") == estado]

    return alumnos


def get_student_by_id(student_id):
    return next((a for a in ALUMNOS if a["id"] == student_id), None)


def get_teachers():
    return PROFESORES


# ──────────────────────────────────────────────
# EVENTOS Y AVISOS
# ──────────────────────────────────────────────

def _event_mysql_to_dict(row):
    fecha = row["data_evento"]

    return {
        "id": row["id"],
        "titulo": row["titulo"],
        "descripcion": row.get("descripcion") or "",
        "fecha": fecha,
        "hora": str(row["hora"])[:5] if row.get("hora") else "",
        "tipo": row.get("tipo") or "aviso",
    }


def get_events(limit=None):
    """
    Devuelve eventos desde MySQL.
    Si falla o no hay eventos, usa EVENTOS mock.
    """
    try:
        sql = """
            SELECT
                id,
                titulo,
                descripcion,
                data_evento,
                hora,
                tipo
            FROM eventos
            ORDER BY data_evento ASC, hora ASC
        """

        params = {}

        if limit:
            sql += " LIMIT :limit"
            params["limit"] = limit

        rows = db.session.execute(text(sql), params).mappings().all()
        eventos = [_event_mysql_to_dict(row) for row in rows]

        if eventos:
            return eventos

    except Exception as e:
        print("Error cargando eventos desde MySQL:", e)

    # Fallback mock
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
    return sorted(get_events(), key=lambda e: str(e.get("fecha", "")))


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
    De momento usa mock hasta crear administración real.
    """
    enrollments = []

    for alumno in ALUMNOS:
        for curso_id in alumno.get("cursos", []):
            curso = get_course_by_id(curso_id)

            if curso:
                enrollments.append({
                    "alumno": alumno["nombre"],
                    "alumno_estado": alumno["estado"],
                    "curso": curso["titulo"],
                    "tutor": curso.get("tutor") or curso.get("profesor") or "Prof. Albino de Matos",
                })

    return enrollments


# ──────────────────────────────────────────────
# UTILIDADES
# ──────────────────────────────────────────────

def format_date(iso_value):
    """
    Formatea una fecha larga.
    Acepta string YYYY-MM-DD o date.
    """
    try:
        if isinstance(iso_value, date):
            d = iso_value
        else:
            d = datetime.strptime(str(iso_value), "%Y-%m-%d").date()

        meses = [
            "enero", "febrero", "marzo", "abril", "mayo", "junio",
            "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
        ]

        return f"{d.day} de {meses[d.month - 1]} de {d.year}"

    except Exception:
        return str(iso_value)


def format_date_short(iso_value):
    """
    Formatea una fecha corta para sidebar/eventos.
    Acepta string YYYY-MM-DD o date.
    """
    try:
        if isinstance(iso_value, date):
            d = iso_value
        else:
            d = datetime.strptime(str(iso_value), "%Y-%m-%d").date()

        meses = [
            "ene", "feb", "mar", "abr", "may", "jun",
            "jul", "ago", "sep", "oct", "nov", "dic"
        ]

        return f"{d.day:02d} {meses[d.month - 1].upper()}"

    except Exception:
        return str(iso_value)


def tipo_icono(tipo):
    return {
        "video": "▶",
        "pdf": "📄",
        "tarea": "✏",
        "test": "✅",
        "foro": "💬",
    }.get(tipo, "◈")


def tipo_css_class(tipo):
    return {
        "video": "ai-video",
        "pdf": "ai-pdf",
        "tarea": "ai-tarea",
        "test": "ai-test",
        "foro": "ai-foro",
    }.get(tipo, "ai-video")


def estado_curso_badge(estado):
    return {
        "en-progreso": ("status-en-progreso", "En progreso"),
        "ativo": ("status-en-progreso", "En progreso"),
        "completado": ("status-completado", "Completado"),
        "concluido": ("status-completado", "Completado"),
        "no-comenzado": ("status-no-comenzado", "No comenzado"),
        "pendente": ("status-no-comenzado", "Pendiente"),
    }.get(estado, ("status-no-comenzado", estado))


def badge_estado(estado):
    return {
        "completado": ("ab-completado", "Completado"),
        "pendiente": ("ab-pendiente", "Pendiente"),
        "pendente": ("ab-pendiente", "Pendiente"),
        "bloqueado": ("ab-bloqueado", "Bloqueado"),
        "no-comenzado": ("ab-no-comenzado", "No comenzado"),
        "abierto": ("ab-abierto", "Abierto"),
        "ativo": ("ab-abierto", "Activo"),
    }.get(estado, ("ab-no-comenzado", estado))


# ──────────────────────────────────────────────
# ÁREAS INSTITUCIONALES / PORTAL
# ──────────────────────────────────────────────

def get_areas_moodle(tipo=None):
    """
    Áreas institucionales del campus desde MySQL.

    Usa la tabla areas_institucionais creada para el portal.
    """
    try:
        sql = """
            SELECT
                id,
                slug,
                titulo,
                descricao,
                conteudo,
                ativo
            FROM areas_institucionais
            WHERE ativo = 1
            ORDER BY id ASC
        """

        rows = db.session.execute(text(sql)).mappings().all()

        areas = []

        for row in rows:
            area = {
                "id": row["id"],
                "slug": row["slug"],
                "nombre": row["titulo"],
                "titulo": row["titulo"],
                "descripcion": row.get("descricao") or "",
                "conteudo": row.get("conteudo") or "",
                "icono": "📘",
                "tipo": "institucional",
                "orden": row["id"],
                "restringido": row["slug"] == "area-docente",
            }

            if not tipo or area["tipo"] == tipo:
                areas.append(area)

        if areas:
            return areas

    except Exception as e:
        print("Error cargando áreas desde MySQL:", e)

    return []


def get_area_by_slug(slug):
    try:
        row = db.session.execute(
            text("""
                SELECT
                    id,
                    slug,
                    titulo,
                    descricao,
                    conteudo,
                    ativo
                FROM areas_institucionais
                WHERE slug = :slug
                  AND ativo = 1
                LIMIT 1
            """),
            {"slug": slug}
        ).mappings().first()

        if row:
            return {
                "id": row["id"],
                "slug": row["slug"],
                "nombre": row["titulo"],
                "titulo": row["titulo"],
                "descripcion": row.get("descricao") or "",
                "conteudo": row.get("conteudo") or "",
                "icono": "📘",
                "tipo": "institucional",
                "orden": row["id"],
                "restringido": row["slug"] == "area-docente",
            }

    except Exception as e:
        print("Error cargando área por slug desde MySQL:", e)

    return None


def get_documentos_by_area(area_slug):
    """
    De momento no hay tabla de documentos institucionales.
    Devuelve lista vacía para que no rompa el portal.
    """
    return []


# ──────────────────────────────────────────────
# CICLOS FORMATIVOS
# ──────────────────────────────────────────────

def _ciclos_fallback():
    return [
        {
            "id": 1,
            "codigo": "CP-AMC",
            "nombre": "Curso Profissional - Animação e Mediação Comunitária",
            "area": "social",
            "nivel": "Nível 4",
            "duracion": "3 anos",
            "descripcion": "Curso profissional orientado para intervenção comunitária, animação sociocultural e mediação.",
        },
        {
            "id": 2,
            "codigo": "CP-CIND",
            "nombre": "Curso Profissional - Construção Industrial",
            "area": "industrial",
            "nivel": "Nível 4",
            "duracion": "3 anos",
            "descripcion": "Formação na área da construção industrial, processos técnicos e segurança.",
        },
        {
            "id": 3,
            "codigo": "CP-DPMM",
            "nombre": "Curso Profissional - Desenho de Produto em Madeira e Mobiliário",
            "area": "madeira",
            "nivel": "Nível 4",
            "duracion": "3 anos",
            "descripcion": "Desenho de produto, mobiliário, materiais e soluções ligadas à madeira.",
        },
        {
            "id": 4,
            "codigo": "CP-DIE",
            "nombre": "Curso Profissional - Design de Interiores e Exteriores",
            "area": "design",
            "nivel": "Nível 4",
            "duracion": "3 anos",
            "descripcion": "Projeto de espaços interiores e exteriores, representação visual e materiais.",
        },
        {
            "id": 5,
            "codigo": "CP-DEQ",
            "nombre": "Curso Profissional - Design de Equipamentos",
            "area": "design",
            "nivel": "Nível 4",
            "duracion": "3 anos",
            "descripcion": "Design de equipamentos, ergonomia, materiais e desenvolvimento de produto.",
        },
        {
            "id": 6,
            "codigo": "CP-IE",
            "nombre": "Curso Profissional - Instalações Elétricas",
            "area": "industrial",
            "nivel": "Nível 4",
            "duracion": "3 anos",
            "descripcion": "Eletricidade, instalações, manutenção, segurança e sistemas elétricos.",
        },
        {
            "id": 7,
            "codigo": "CP-PMCNC",
            "nombre": "Curso Profissional - Programação e Maquinação CNC",
            "area": "industrial",
            "nivel": "Nível 4",
            "duracion": "3 anos",
            "descripcion": "Programação, maquinação CNC, CAD/CAM e controlo de produção.",
        },
        {
            "id": 8,
            "codigo": "CP-SCR",
            "nombre": "Curso Profissional - Sistemas de Computação e Redes",
            "area": "informatica",
            "nivel": "Nível 4",
            "duracion": "3 anos",
            "descripcion": "Redes, sistemas, hardware, administração e suporte informático.",
        },
        {
            "id": 9,
            "codigo": "EFA-AG",
            "nombre": "Curso EFA - Agente em Geriatria",
            "area": "efa",
            "nivel": "EFA",
            "duracion": "Adultos",
            "descripcion": "Educação e Formação de Adultos na área de geriatria.",
        },
        {
            "id": 10,
            "codigo": "EFA-CSD",
            "nombre": "Curso EFA - Comunicação e Serviço Digital",
            "area": "efa",
            "nivel": "EFA",
            "duracion": "Adultos",
            "descripcion": "Comunicação digital, ferramentas tecnológicas e serviços digitais.",
        },
        {
            "id": 11,
            "codigo": "EFA-IIGR",
            "nombre": "Curso EFA - Informática - Instalação e Gestão de Redes",
            "area": "efa",
            "nivel": "EFA",
            "duracion": "Adultos",
            "descripcion": "Instalação, manutenção e gestão de redes.",
        },
        {
            "id": 12,
            "codigo": "EFA-DMCM",
            "nombre": "Curso EFA - Desenho de Mobiliário e Construções em Madeira",
            "area": "efa",
            "nivel": "EFA",
            "duracion": "Adultos",
            "descripcion": "Desenho de mobiliário, construção em madeira e processos técnicos.",
        },
    ]


def _ciclo_mysql_to_dict(row):
    return {
        "id": row["id"],
        "codigo": row["codigo"],
        "nombre": row["nombre"],
        "area": row["area"],
        "nivel": row["nivel"],
        "duracion": row["duracion"],
        "descripcion": row["descripcion"],
    }


def get_ciclos_formativos(area=None):
    """
    Devuelve ciclos formativos desde MySQL.
    Si algo falla, usa fallback.
    """
    try:
        sql = """
            SELECT
                id,
                codigo,
                nombre,
                area,
                nivel,
                duracion,
                descripcion
            FROM ciclos_formativos
            WHERE activo = 1
        """

        params = {}

        if area:
            sql += " AND area = :area"
            params["area"] = area

        sql += " ORDER BY orden ASC, id ASC"

        rows = db.session.execute(text(sql), params).mappings().all()
        ciclos = [_ciclo_mysql_to_dict(row) for row in rows]

        if ciclos:
            return ciclos

    except Exception as e:
        print("Error cargando ciclos desde MySQL:", e)

    data = _ciclos_fallback()

    if area:
        return [c for c in data if c["area"] == area]

    return data


def get_ciclo_by_id(ciclo_id):
    """
    Devuelve un ciclo con sus años, asignaturas, FCT y PAP desde MySQL.
    Si algo falla, usa fallback.
    """
    try:
        ciclo_row = db.session.execute(
            text("""
                SELECT
                    id,
                    codigo,
                    nombre,
                    area,
                    nivel,
                    duracion,
                    descripcion
                FROM ciclos_formativos
                WHERE id = :ciclo_id
                  AND activo = 1
                LIMIT 1
            """),
            {"ciclo_id": ciclo_id}
        ).mappings().first()

        if not ciclo_row:
            return _get_ciclo_fallback_by_id(ciclo_id)

        ciclo = _ciclo_mysql_to_dict(ciclo_row)
        ciclo["anos"] = []

        anos_rows = db.session.execute(
            text("""
                SELECT
                    id,
                    numero,
                    ano_escolar,
                    descripcion
                FROM anos_ciclo
                WHERE ciclo_id = :ciclo_id
                ORDER BY orden ASC, numero ASC
            """),
            {"ciclo_id": ciclo_id}
        ).mappings().all()

        for ano_row in anos_rows:
            ano = {
                "id": ano_row["id"],
                "numero": ano_row["numero"],
                "ano_escolar": ano_row["ano_escolar"],
                "descripcion": ano_row["descripcion"],
                "disciplinas": [],
            }

            disciplinas_rows = db.session.execute(
                text("""
                    SELECT
                        id,
                        codigo,
                        nombre,
                        tipo,
                        horas,
                        descripcion
                    FROM disciplinas_ciclo
                    WHERE ano_id = :ano_id
                    ORDER BY orden ASC, id ASC
                """),
                {"ano_id": ano_row["id"]}
            ).mappings().all()

            for disciplina_row in disciplinas_rows:
                ano["disciplinas"].append({
                    "id": disciplina_row["id"],
                    "codigo": disciplina_row["codigo"],
                    "nombre": disciplina_row["nombre"],
                    "tipo": disciplina_row["tipo"],
                    "horas": disciplina_row["horas"],
                    "descripcion": disciplina_row["descripcion"],
                })

            ciclo["anos"].append(ano)

        return ciclo

    except Exception as e:
        print("Error cargando ciclo por ID desde MySQL:", e)
        return _get_ciclo_fallback_by_id(ciclo_id)


def _get_ciclo_fallback_by_id(ciclo_id):
    ciclo = next((c for c in _ciclos_fallback() if c["id"] == ciclo_id), None)

    if not ciclo:
        return None

    ciclo = dict(ciclo)

    ciclo["anos"] = [
        {
            "numero": 1,
            "ano_escolar": "10º ano",
            "disciplinas": [
                {"nombre": "Português", "tipo": "disciplina"},
                {"nombre": "Inglês", "tipo": "disciplina"},
                {"nombre": "Área de Integração", "tipo": "disciplina"},
                {"nombre": "Formação Técnica I", "tipo": "disciplina"},
            ],
        },
        {
            "numero": 2,
            "ano_escolar": "11º ano",
            "disciplinas": [
                {"nombre": "Português", "tipo": "disciplina"},
                {"nombre": "Inglês Técnico", "tipo": "disciplina"},
                {"nombre": "Área de Integração", "tipo": "disciplina"},
                {"nombre": "Formação Técnica II", "tipo": "disciplina"},
            ],
        },
        {
            "numero": 3,
            "ano_escolar": "12º ano",
            "disciplinas": [
                {"nombre": "Formação Técnica III", "tipo": "disciplina"},
                {"nombre": "FCT — Formação em Contexto de Trabalho", "tipo": "fct"},
                {"nombre": "PAP — Prova de Aptidão Profissional", "tipo": "pap"},
            ],
        },
    ]

    return ciclo

    # ──────────────────────────────────────────────
# DETALLE DE DISCIPLINA / ASIGNATURA
# ──────────────────────────────────────────────

def get_disciplina_by_id(disciplina_id):
    """
    Devuelve una disciplina/asignatura con su ciclo, año, secciones y recursos.
    """
    try:
        disciplina_row = db.session.execute(
            text("""
                SELECT
                    d.id,
                    d.codigo,
                    d.nombre,
                    d.tipo,
                    d.horas,
                    d.descripcion,
                    a.id AS ano_id,
                    a.numero AS ano_numero,
                    a.ano_escolar,
                    c.id AS ciclo_id,
                    c.codigo AS ciclo_codigo,
                    c.nombre AS ciclo_nombre,
                    c.area AS ciclo_area,
                    c.nivel AS ciclo_nivel,
                    c.duracion AS ciclo_duracion
                FROM disciplinas_ciclo d
                JOIN anos_ciclo a ON a.id = d.ano_id
                JOIN ciclos_formativos c ON c.id = a.ciclo_id
                WHERE d.id = :disciplina_id
                LIMIT 1
            """),
            {"disciplina_id": disciplina_id}
        ).mappings().first()

        if not disciplina_row:
            return None

        disciplina = {
            "id": disciplina_row["id"],
            "codigo": disciplina_row["codigo"],
            "nombre": disciplina_row["nombre"],
            "tipo": disciplina_row["tipo"],
            "horas": disciplina_row["horas"],
            "descripcion": disciplina_row["descripcion"],
            "ano": {
                "id": disciplina_row["ano_id"],
                "numero": disciplina_row["ano_numero"],
                "ano_escolar": disciplina_row["ano_escolar"],
            },
            "ciclo": {
                "id": disciplina_row["ciclo_id"],
                "codigo": disciplina_row["ciclo_codigo"],
                "nombre": disciplina_row["ciclo_nombre"],
                "area": disciplina_row["ciclo_area"],
                "nivel": disciplina_row["ciclo_nivel"],
                "duracion": disciplina_row["ciclo_duracion"],
            },
            "secciones": [],
        }

        secciones_rows = db.session.execute(
            text("""
                SELECT
                    id,
                    titulo,
                    slug,
                    descripcion,
                    orden
                FROM secciones_disciplina
                WHERE disciplina_id = :disciplina_id
                  AND visible = 1
                ORDER BY orden ASC, id ASC
            """),
            {"disciplina_id": disciplina_id}
        ).mappings().all()

        for seccion_row in secciones_rows:
            seccion = {
                "id": seccion_row["id"],
                "titulo": seccion_row["titulo"],
                "slug": seccion_row["slug"],
                "descripcion": seccion_row["descripcion"],
                "orden": seccion_row["orden"],
                "recursos": [],
            }

            recursos_rows = db.session.execute(
                text("""
                    SELECT
                        id,
                        titulo,
                        tipo,
                        descripcion,
                        url,
                        orden
                    FROM recursos_disciplina
                    WHERE seccion_id = :seccion_id
                      AND visible = 1
                    ORDER BY orden ASC, id ASC
                """),
                {"seccion_id": seccion_row["id"]}
            ).mappings().all()

            for recurso_row in recursos_rows:
                tipo = recurso_row["tipo"]

                seccion["recursos"].append({
                    "id": recurso_row["id"],
                    "titulo": recurso_row["titulo"],
                    "tipo": tipo,
                    "descripcion": recurso_row["descripcion"],
                    "url": recurso_row["url"],
                    "orden": recurso_row["orden"],
                    "_icono": recurso_icono(tipo),
                    "_badge": recurso_badge(tipo),
                })

            disciplina["secciones"].append(seccion)

        return disciplina

    except Exception as e:
        print("Error cargando disciplina desde MySQL:", e)
        return None


def recurso_icono(tipo):
    return {
        "documento": "📄",
        "video": "▶",
        "lectura": "📖",
        "tarea": "✏",
        "foro": "💬",
        "cuestionario": "✅",
        "evidencia": "📁",
        "enlace": "🔗",
    }.get(tipo, "📌")


def recurso_badge(tipo):
    return {
        "documento": "DOCUMENTO",
        "video": "VÍDEO",
        "lectura": "LECTURA",
        "tarea": "TAREA",
        "foro": "FORO",
        "cuestionario": "CUESTIONARIO",
        "evidencia": "EVIDENCIA",
        "enlace": "ENLACE",
    }.get(tipo, tipo.upper() if tipo else "RECURSO")
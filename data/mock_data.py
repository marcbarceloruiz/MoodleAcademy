"""
Datos simulados de Academia Vertice.
Sustituyen al antiguo data.js del frontend.
Aquí se definen usuarios, cursos, módulos, actividades,
alumnos, profesores, eventos, avisos y estadísticas.
"""

# ──────────────────────────────────────────────
# USUARIO ACTUAL
# ──────────────────────────────────────────────

USUARIO = {
    "id": 1,
    "nombre": "Natachinha",
    "email": "natacha.antunes@academiavertice.pt",
    "iniciales": "NA",
    "rol": "professora",
    "matriculas": [1, 2, 3],
}

# ──────────────────────────────────────────────
# CURSOS
# ──────────────────────────────────────────────

CURSOS = [
    {
        "id": 1,
        "titulo": "Inglés B2: Upper Intermediate",
        "categoria": "idiomas",
        "tutor": "Sarah Mitchell",
        "inicio": "2024-09-15",
        "fin": "2025-06-20",
        "estado": "en-progreso",
        "imagen": "1",
        "progreso": 62,
        "descripcion": "Curso de inglés nivel B2 orientado a la comunicación profesional y académica.",
        "modulos": [
            {
                "id": "m1",
                "titulo": "Módulo 1: Grammar & Vocabulary",
                "actividades": [
                    {"id": "a1", "titulo": "Present Perfect vs Past Simple", "tipo": "video", "duracion": "18 min", "estado": "completado"},
                    {"id": "a2", "titulo": "Vocabulary in Context", "tipo": "pdf", "duracion": "PDF", "estado": "completado"},
                    {"id": "a3", "titulo": "Grammar Practice Test", "tipo": "test", "duracion": "20 min", "estado": "completado"},
                ],
            },
            {
                "id": "m2",
                "titulo": "Módulo 2: Reading & Writing",
                "actividades": [
                    {"id": "a4", "titulo": "Academic Reading Strategies", "tipo": "video", "duracion": "22 min", "estado": "completado"},
                    {"id": "a5", "titulo": "Essay Writing Guide", "tipo": "pdf", "duracion": "PDF", "estado": "pendiente"},
                    {"id": "a6", "titulo": "Tarea: Write a formal email", "tipo": "tarea", "duracion": "Entrega", "estado": "pendiente"},
                ],
            },
            {
                "id": "m3",
                "titulo": "Módulo 3: Speaking & Listening",
                "actividades": [
                    {"id": "a7", "titulo": "Pronunciation Workshop", "tipo": "video", "duracion": "30 min", "estado": "no-comenzado"},
                    {"id": "a8", "titulo": "Listening Comprehension", "tipo": "test", "duracion": "25 min", "estado": "bloqueado"},
                    {"id": "a9", "titulo": "Foro: Debate topics", "tipo": "foro", "duracion": "Foro", "estado": "bloqueado"},
                ],
            },
        ],
    },
    {
        "id": 2,
        "titulo": "Técnico en Cuidados Auxiliares de Enfermería",
        "categoria": "sanitario",
        "tutor": "Dra. Carmen Vidal",
        "inicio": "2024-10-01",
        "fin": "2025-07-15",
        "estado": "en-progreso",
        "imagen": "2",
        "progreso": 38,
        "descripcion": "Formación profesional en cuidados básicos de enfermería y atención al paciente.",
        "modulos": [
            {
                "id": "m1",
                "titulo": "Módulo 1: Anatomía y Fisiología",
                "actividades": [
                    {"id": "a1", "titulo": "Introducción al cuerpo humano", "tipo": "video", "duracion": "25 min", "estado": "completado"},
                    {"id": "a2", "titulo": "Sistema cardiovascular", "tipo": "video", "duracion": "30 min", "estado": "completado"},
                    {"id": "a3", "titulo": "Apuntes Anatomía básica", "tipo": "pdf", "duracion": "PDF", "estado": "completado"},
                    {"id": "a4", "titulo": "Test: Anatomía básica", "tipo": "test", "duracion": "20 min", "estado": "pendiente"},
                ],
            },
            {
                "id": "m2",
                "titulo": "Módulo 2: Técnicas de Enfermería",
                "actividades": [
                    {"id": "a5", "titulo": "Toma de constantes vitales", "tipo": "video", "duracion": "20 min", "estado": "no-comenzado"},
                    {"id": "a6", "titulo": "Protocolo de higiene hospitalaria", "tipo": "pdf", "duracion": "PDF", "estado": "bloqueado"},
                    {"id": "a7", "titulo": "Tarea: Caso clínico", "tipo": "tarea", "duracion": "Entrega", "estado": "bloqueado"},
                ],
            },
        ],
    },
    {
        "id": 3,
        "titulo": "FP: Administración y Finanzas",
        "categoria": "fp",
        "tutor": "Prof. Marcos Herrera",
        "inicio": "2025-01-10",
        "fin": "2025-12-20",
        "estado": "no-comenzado",
        "imagen": "3",
        "progreso": 0,
        "descripcion": "Ciclo formativo de grado superior en administración, contabilidad y finanzas empresariales.",
        "modulos": [
            {
                "id": "m1",
                "titulo": "Módulo 1: Contabilidad General",
                "actividades": [
                    {"id": "a1", "titulo": "Introducción a la contabilidad", "tipo": "video", "duracion": "20 min", "estado": "no-comenzado"},
                    {"id": "a2", "titulo": "El plan general contable", "tipo": "pdf", "duracion": "PDF", "estado": "bloqueado"},
                ],
            },
        ],
    },
    {
        "id": 4,
        "titulo": "Francés A1-A2: Iniciación",
        "categoria": "idiomas",
        "tutor": "Marie Leclerc",
        "inicio": "2025-02-01",
        "fin": "2025-08-30",
        "estado": "no-comenzado",
        "imagen": "4",
        "progreso": 0,
        "descripcion": "Introducción al idioma francés desde cero hasta nivel A2 del Marco Europeo.",
        "modulos": [
            {
                "id": "m1",
                "titulo": "Módulo 1: Phonétique et salutations",
                "actividades": [
                    {"id": "a1", "titulo": "Les sons du français", "tipo": "video", "duracion": "15 min", "estado": "no-comenzado"},
                    {"id": "a2", "titulo": "Fiche de vocabulaire", "tipo": "pdf", "duracion": "PDF", "estado": "bloqueado"},
                ],
            },
        ],
    },
    {
        "id": 5,
        "titulo": "Atención Sociosanitaria a Personas Dependientes",
        "categoria": "sanitario",
        "tutor": "Enf. Patricia Solano",
        "inicio": "2024-11-01",
        "fin": "2025-09-30",
        "estado": "en-progreso",
        "imagen": "5",
        "progreso": 55,
        "descripcion": "Formación en atención y apoyo a personas en situación de dependencia.",
        "modulos": [
            {
                "id": "m1",
                "titulo": "Módulo 1: Marco legal y ético",
                "actividades": [
                    {"id": "a1", "titulo": "Ley de Dependencia", "tipo": "pdf", "duracion": "PDF", "estado": "completado"},
                    {"id": "a2", "titulo": "Ética en el cuidado", "tipo": "video", "duracion": "20 min", "estado": "completado"},
                    {"id": "a3", "titulo": "Test: Marco legal", "tipo": "test", "duracion": "15 min", "estado": "pendiente"},
                ],
            },
        ],
    },
]

# ──────────────────────────────────────────────
# ALUMNOS
# ──────────────────────────────────────────────

ALUMNOS = [
    {"id": 1,  "nombre": "Ana García López",      "email": "ana.garcia@mail.com",      "dni": "12345678A", "cursos": [1, 2], "asistencia": 92, "estado": "activo",    "ultimaConexion": "2025-05-20"},
    {"id": 2,  "nombre": "Carlos Martínez",        "email": "carlos.m@mail.com",        "dni": "23456789B", "cursos": [1, 3], "asistencia": 78, "estado": "activo",    "ultimaConexion": "2025-05-19"},
    {"id": 3,  "nombre": "Lucía Fernández",        "email": "lucia.f@mail.com",         "dni": "34567890C", "cursos": [2],    "asistencia": 55, "estado": "pendiente", "ultimaConexion": "2025-05-10"},
    {"id": 4,  "nombre": "Pedro Sánchez Ruiz",     "email": "pedro.s@mail.com",         "dni": "45678901D", "cursos": [1, 5], "asistencia": 88, "estado": "activo",    "ultimaConexion": "2025-05-21"},
    {"id": 5,  "nombre": "María Torres",           "email": "maria.t@mail.com",         "dni": "56789012E", "cursos": [3, 4], "asistencia": 43, "estado": "inactivo",  "ultimaConexion": "2025-04-28"},
    {"id": 6,  "nombre": "Diego Romero",           "email": "diego.r@mail.com",         "dni": "67890123F", "cursos": [2, 5], "asistencia": 95, "estado": "activo",    "ultimaConexion": "2025-05-22"},
    {"id": 7,  "nombre": "Elena Moreno",           "email": "elena.m@mail.com",         "dni": "78901234G", "cursos": [1],    "asistencia": 71, "estado": "activo",    "ultimaConexion": "2025-05-18"},
    {"id": 8,  "nombre": "Javier Jiménez",         "email": "javier.j@mail.com",        "dni": "89012345H", "cursos": [3],    "asistencia": 60, "estado": "pendiente", "ultimaConexion": "2025-05-12"},
    {"id": 9,  "nombre": "Sara López Gil",         "email": "sara.l@mail.com",          "dni": "90123456I", "cursos": [4, 5], "asistencia": 83, "estado": "activo",    "ultimaConexion": "2025-05-20"},
    {"id": 10, "nombre": "Pablo Navarro",          "email": "pablo.n@mail.com",         "dni": "01234567J", "cursos": [1, 2], "asistencia": 97, "estado": "activo",    "ultimaConexion": "2025-05-22"},
]

# ──────────────────────────────────────────────
# PROFESORES
# ──────────────────────────────────────────────

PROFESORES = [
    {"id": 1, "nombre": "Sarah Mitchell",      "email": "sarah.m@academiavertice.es",   "especialidad": "Inglés",            "cursos": [1],    "estado": "activo"},
    {"id": 2, "nombre": "Dra. Carmen Vidal",   "email": "carmen.v@academiavertice.es",  "especialidad": "Enfermería",        "cursos": [2],    "estado": "activo"},
    {"id": 3, "nombre": "Prof. Marcos Herrera","email": "marcos.h@academiavertice.es",  "especialidad": "Administración",   "cursos": [3],    "estado": "activo"},
    {"id": 4, "nombre": "Marie Leclerc",       "email": "marie.l@academiavertice.es",   "especialidad": "Francés",           "cursos": [4],    "estado": "activo"},
    {"id": 5, "nombre": "Enf. Patricia Solano","email": "patricia.s@academiavertice.es","especialidad": "Sociosanitario",    "cursos": [5],    "estado": "activo"},
    {"id": 6, "nombre": "Natacha Antunes",     "email": "natacha.antunes@academiavertice.pt", "especialidad": "Coordinación","cursos": [1,2,3],"estado": "activo"},
]

# ──────────────────────────────────────────────
# EVENTOS
# ──────────────────────────────────────────────

EVENTOS = [
    {"id": 1,  "titulo": "Entrega: Essay formal email",       "fecha": "2025-05-30", "hora": "23:59", "tipo": "tarea",   "cursoId": 1},
    {"id": 2,  "titulo": "Test: Anatomía básica",             "fecha": "2025-06-03", "hora": "10:00", "tipo": "test",    "cursoId": 2},
    {"id": 3,  "titulo": "Tutoría grupal — Inglés B2",        "fecha": "2025-06-05", "hora": "17:00", "tipo": "tutoria", "cursoId": 1},
    {"id": 4,  "titulo": "Seminario: Atención al paciente",   "fecha": "2025-06-10", "hora": "09:00", "tipo": "evento",  "cursoId": 2},
    {"id": 5,  "titulo": "Inicio Módulo 3 — Inglés",          "fecha": "2025-06-12", "hora": "00:00", "tipo": "evento",  "cursoId": 1},
    {"id": 6,  "titulo": "Reunión de claustro",               "fecha": "2025-06-15", "hora": "11:00", "tipo": "admin",   "cursoId": None},
    {"id": 7,  "titulo": "Examen parcial — FP Admin",         "fecha": "2025-06-20", "hora": "09:00", "tipo": "examen",  "cursoId": 3},
    {"id": 8,  "titulo": "Fin plazo matrículas septiembre",   "fecha": "2025-06-25", "hora": "14:00", "tipo": "admin",   "cursoId": None},
]

# ──────────────────────────────────────────────
# AVISOS
# ──────────────────────────────────────────────

AVISOS = [
    {"id": 1, "titulo": "Actualización de la plataforma el 1 de junio",  "fecha": "2025-05-20", "tipo": "sistema",    "importante": True},
    {"id": 2, "titulo": "Nueva normativa de evaluación continua 2024/25", "fecha": "2025-05-15", "tipo": "normativa",  "importante": True},
    {"id": 3, "titulo": "Horario de secretaría en período de exámenes",   "fecha": "2025-05-10", "tipo": "info",       "importante": False},
    {"id": 4, "titulo": "Recordatorio: cierre del aula virtual en agosto","fecha": "2025-05-05", "tipo": "sistema",    "importante": False},
]

# ──────────────────────────────────────────────
# ESTADÍSTICAS DE ADMINISTRACIÓN
# ──────────────────────────────────────────────

ESTADISTICAS = {
    "totalAlumnos":     len(ALUMNOS),
    "totalProfesores":  len(PROFESORES),
    "totalCursos":      len(CURSOS),
    "totalMatriculas":  sum(len(a["cursos"]) for a in ALUMNOS),
    "asistenciaHoy":    81,
}

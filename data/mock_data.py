"""
Dados simulados — Academia Profissional Prof. Albino de Matos.
Usados como fallback quando MySQL não está disponível.
Todos os dados são genéricos e orientados ao campus real.
"""

# ──────────────────────────────────────────────
# UTILIZADOR (fallback — sobreposto pela sessão)
# ──────────────────────────────────────────────

USUARIO = {
    "id": None,
    "nombre": "",
    "nome": "",
    "email": "",
    "iniciales": "V",
    "rol": "visitante",
    "matriculas": [1, 2, 3],
}

# ──────────────────────────────────────────────
# CURSOS
# ──────────────────────────────────────────────

CURSOS = [
    {
        "id": 1,
        "titulo": "Curso Profissional — Animação e Mediação Comunitária",
        "categoria": "social",
        "tutor": "Formador AMC",
        "inicio": "2025-09-16",
        "fin": "2026-06-26",
        "estado": "en-progreso",
        "imagen": "1",
        "progreso": 68,
        "descripcion": "Ciclo de nível 4 orientado para a animação sociocultural, mediação comunitária e organização de eventos.",
        "modulos": [
            {
                "id": "m1",
                "titulo": "Módulo 1 — Animação Sociocultural: Fundamentos",
                "actividades": [
                    {"id": "a1", "titulo": "Introdução à animação sociocultural", "tipo": "video",  "duracion": "20 min", "estado": "completado"},
                    {"id": "a2", "titulo": "Guia de atividades comunitárias",      "tipo": "pdf",    "duracion": "PDF",    "estado": "completado"},
                    {"id": "a3", "titulo": "Teste: Conceitos base de animação",    "tipo": "test",   "duracion": "15 min", "estado": "completado"},
                ],
            },
            {
                "id": "m2",
                "titulo": "Módulo 2 — Mediação e Resolução de Conflitos",
                "actividades": [
                    {"id": "a4", "titulo": "Técnicas de mediação comunitária",     "tipo": "video",  "duracion": "25 min", "estado": "completado"},
                    {"id": "a5", "titulo": "Manual do mediador",                   "tipo": "pdf",    "duracion": "PDF",    "estado": "pendiente"},
                    {"id": "a6", "titulo": "Trabalho: Análise de caso real",       "tipo": "tarea",  "duracion": "Entrega","estado": "pendiente"},
                ],
            },
            {
                "id": "m3",
                "titulo": "Módulo 3 — Organização de Eventos Culturais",
                "actividades": [
                    {"id": "a7", "titulo": "Planificação e logística de eventos",  "tipo": "video",  "duracion": "30 min", "estado": "no-comenzado"},
                    {"id": "a8", "titulo": "Ficha técnica de evento",             "tipo": "pdf",    "duracion": "PDF",    "estado": "bloqueado"},
                    {"id": "a9", "titulo": "Fórum: Partilha de experiências",     "tipo": "foro",   "duracion": "Fórum",  "estado": "bloqueado"},
                ],
            },
        ],
    },
    {
        "id": 2,
        "titulo": "Curso Profissional — Sistemas de Computação e Redes",
        "categoria": "informatica",
        "tutor": "Formador CTE",
        "inicio": "2025-09-16",
        "fin": "2026-06-26",
        "estado": "en-progreso",
        "imagen": "2",
        "progreso": 54,
        "descripcion": "Ciclo de nível 4 em administração de sistemas, redes locais e cibersegurança.",
        "modulos": [
            {
                "id": "m1",
                "titulo": "Módulo 1 — Sistemas Operativos e Redes Locais",
                "actividades": [
                    {"id": "a1", "titulo": "Arquitetura de sistemas operativos",  "tipo": "video",  "duracion": "22 min", "estado": "completado"},
                    {"id": "a2", "titulo": "Redes TCP/IP — Fundamentos",          "tipo": "pdf",    "duracion": "PDF",    "estado": "completado"},
                    {"id": "a3", "titulo": "Teste: Redes e protocolos",            "tipo": "test",   "duracion": "20 min", "estado": "pendiente"},
                ],
            },
            {
                "id": "m2",
                "titulo": "Módulo 2 — Administração de Servidores",
                "actividades": [
                    {"id": "a4", "titulo": "Instalação e configuração de servidor","tipo": "video",  "duracion": "35 min", "estado": "no-comenzado"},
                    {"id": "a5", "titulo": "Manual de administração Linux",        "tipo": "pdf",    "duracion": "PDF",    "estado": "bloqueado"},
                    {"id": "a6", "titulo": "Projeto: Configuração de servidor",    "tipo": "tarea",  "duracion": "Entrega","estado": "bloqueado"},
                ],
            },
        ],
    },
    {
        "id": 3,
        "titulo": "EFA — Comunicação e Serviço Digital",
        "categoria": "efa",
        "tutor": "Formador EFA",
        "inicio": "2026-01-12",
        "fin": "2026-12-18",
        "estado": "no-comenzado",
        "imagen": "3",
        "progreso": 0,
        "descripcion": "Percurso EFA com competências em comunicação digital, redes sociais e serviços online.",
        "modulos": [
            {
                "id": "m1",
                "titulo": "Módulo 1 — Comunicação Digital",
                "actividades": [
                    {"id": "a1", "titulo": "Ferramentas digitais de comunicação", "tipo": "video",  "duracion": "18 min", "estado": "no-comenzado"},
                    {"id": "a2", "titulo": "Guia de comunicação online",          "tipo": "pdf",    "duracion": "PDF",    "estado": "bloqueado"},
                ],
            },
            {
                "id": "m2",
                "titulo": "Módulo 2 — Serviços e Plataformas Online",
                "actividades": [
                    {"id": "a3", "titulo": "Plataformas de colaboração digital",  "tipo": "video",  "duracion": "20 min", "estado": "no-comenzado"},
                    {"id": "a4", "titulo": "Trabalho: Criar presença digital",    "tipo": "tarea",  "duracion": "Entrega","estado": "bloqueado"},
                ],
            },
        ],
    },
]

# ──────────────────────────────────────────────
# ALUNOS (fallback — admin panel)
# ──────────────────────────────────────────────

ALUMNOS = [
    {"id": 1,  "nombre": "Aluno 01 — AMC",        "email": "aluno01@academiaprofissional.pt", "dni": "---", "cursos": [1], "asistencia": 92, "estado": "activo",    "ultimaConexion": "2026-06-07"},
    {"id": 2,  "nombre": "Aluno 02 — AMC",        "email": "aluno02@academiaprofissional.pt", "dni": "---", "cursos": [1], "asistencia": 78, "estado": "activo",    "ultimaConexion": "2026-06-06"},
    {"id": 3,  "nombre": "Aluno 03 — SCR",        "email": "aluno03@academiaprofissional.pt", "dni": "---", "cursos": [2], "asistencia": 65, "estado": "activo",    "ultimaConexion": "2026-06-05"},
    {"id": 4,  "nombre": "Aluno 04 — SCR",        "email": "aluno04@academiaprofissional.pt", "dni": "---", "cursos": [2], "asistencia": 88, "estado": "activo",    "ultimaConexion": "2026-06-07"},
    {"id": 5,  "nombre": "Aluno 05 — EFA",        "email": "aluno05@academiaprofissional.pt", "dni": "---", "cursos": [3], "asistencia": 43, "estado": "pendiente", "ultimaConexion": "2026-05-28"},
    {"id": 6,  "nombre": "Aluno 06 — EFA",        "email": "aluno06@academiaprofissional.pt", "dni": "---", "cursos": [3], "asistencia": 95, "estado": "activo",    "ultimaConexion": "2026-06-07"},
    {"id": 7,  "nombre": "Aluno 07 — AMC",        "email": "aluno07@academiaprofissional.pt", "dni": "---", "cursos": [1], "asistencia": 71, "estado": "activo",    "ultimaConexion": "2026-06-04"},
    {"id": 8,  "nombre": "Aluno 08 — SCR",        "email": "aluno08@academiaprofissional.pt", "dni": "---", "cursos": [2], "asistencia": 60, "estado": "pendiente", "ultimaConexion": "2026-06-01"},
    {"id": 9,  "nombre": "Aluno 09 — EFA",        "email": "aluno09@academiaprofissional.pt", "dni": "---", "cursos": [3], "asistencia": 83, "estado": "activo",    "ultimaConexion": "2026-06-06"},
    {"id": 10, "nombre": "Aluno 10 — AMC",        "email": "aluno10@academiaprofissional.pt", "dni": "---", "cursos": [1], "asistencia": 97, "estado": "activo",    "ultimaConexion": "2026-06-07"},
]

# ──────────────────────────────────────────────
# FORMADORES (fallback — admin panel)
# ──────────────────────────────────────────────

PROFESORES = [
    {"id": 1, "nombre": "Formador AMC",  "email": "formador.amc@academiaprofissional.pt",  "especialidad": "Animação e Mediação Comunitária",  "cursos": [1], "estado": "activo"},
    {"id": 2, "nombre": "Formador CTE",  "email": "formador.cte@academiaprofissional.pt",  "especialidad": "Sistemas de Computação e Redes",   "cursos": [2], "estado": "activo"},
    {"id": 3, "nombre": "Formador EFA",  "email": "formador.efa@academiaprofissional.pt",  "especialidad": "Comunicação e Serviço Digital",    "cursos": [3], "estado": "activo"},
]

# ──────────────────────────────────────────────
# EVENTOS
# ──────────────────────────────────────────────

EVENTOS = [
    {"id": 1, "titulo": "Entrega de trabalho — Área de Integração",     "fecha": "2026-06-15", "hora": "23:59", "tipo": "tarea",   "cursoId": 1},
    {"id": 2, "titulo": "Avaliação de Português",                        "fecha": "2026-06-18", "hora": "09:00", "tipo": "examen",  "cursoId": None},
    {"id": 3, "titulo": "Sessão de orientação PAP",                      "fecha": "2026-06-20", "hora": "14:00", "tipo": "evento",  "cursoId": None},
    {"id": 4, "titulo": "Reunião de acompanhamento FCT",                 "fecha": "2026-06-25", "hora": "10:00", "tipo": "tutoria", "cursoId": None},
    {"id": 5, "titulo": "Atividade EQAVET — Qualidade em Formação",      "fecha": "2026-06-28", "hora": "09:30", "tipo": "evento",  "cursoId": None},
]

# ──────────────────────────────────────────────
# AVISOS
# ──────────────────────────────────────────────

AVISOS = [
    {"id": 1, "titulo": "Atualização do campus virtual — nova interface",       "fecha": "2026-06-01", "tipo": "sistema",   "importante": True},
    {"id": 2, "titulo": "Novo calendário de avaliação 2025/26",                 "fecha": "2026-05-28", "tipo": "normativa", "importante": True},
    {"id": 3, "titulo": "Sessões de acompanhamento pedagógico disponíveis",     "fecha": "2026-05-20", "tipo": "info",      "importante": False},
    {"id": 4, "titulo": "Informação sobre FCT e PAP — 3.º curso",              "fecha": "2026-05-15", "tipo": "info",      "importante": False},
]

# ──────────────────────────────────────────────
# ESTATÍSTICAS DE ADMINISTRAÇÃO
# ──────────────────────────────────────────────

ESTADISTICAS = {
    "totalAlumnos":    len(ALUMNOS),
    "totalProfesores": len(PROFESORES),
    "totalCursos":     len(CURSOS),
    "totalMatriculas": sum(len(a["cursos"]) for a in ALUMNOS),
    "asistenciaHoy":   82,
}

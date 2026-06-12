"""
Blueprint: Portal institucional.
Rotas: /portal  /portal/<area_slug>

Adiciona: novas áreas (CTEs, EFA, FMC), proteção de áreas restritas,
          labels de ação para documentos baseadas na URL.
"""

from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, flash,
)
from services.data_service import (
    get_current_user, get_notices, get_centro,
    format_date, get_areas_moodle,
    get_area_by_slug, get_documentos_by_area,
)

portal_bp = Blueprint("portal", __name__)


# ── Áreas que exigem login de docente ou admin ────────────────
AREAS_RESTRITAS = {
    "area-docente":    ["admin", "docente"],
    "manual-formador": ["admin", "docente"],
}


# ── Aliases de URL ─────────────────────────────────────────────
AREA_ALIASES = {
    "reglamento": "regulamento-interno",
    "reglamento-interno": "regulamento-interno",
    "proyecto-educativo": "projeto-educativo",
    "projeto-educativo": "projeto-educativo",
    "plan-actividades": "plano-atividades",
    "plano-actividades": "plano-atividades",
    "plano-atividades": "plano-atividades",
    "manual-alumno": "manual-aluno",
    "manual-aluno": "manual-aluno",
    "manual-formador": "manual-formador",
    "biblioteca": "biblioteca-digital",
    "biblioteca-digital": "biblioteca-digital",
    "centro-qualifica": "centro-qualifica",
    "eqavet": "eqavet",
    "erasmus": "erasmus",
    "area-docente": "area-docente",
    # Novos
    "centros-tecnologicos": "centros-tecnologicos",
    "cte-informatica": "cte-informatica",
    "cte-industrial": "cte-industrial",
    "efa": "efa",
    "efa-escolar": "efa-escolar",
    "efa-profissional": "efa-profissional",
    "formacao-modular-certificada": "formacao-modular-certificada",
}


# ── Ordem das tarjetas no portal ──────────────────────────────
PORTAL_ORDER = [
    "regulamento-interno", "projeto-educativo", "plano-atividades",
    "eqavet", "erasmus",
    "manual-aluno", "manual-formador",
    "biblioteca-digital", "centro-qualifica", "area-docente",
    # Novos
    "centros-tecnologicos", "cte-informatica", "cte-industrial",
    "efa", "efa-escolar", "efa-profissional",
    "formacao-modular-certificada",
]


# ── Metadados UI (ícone, cor, fallback de docs) ───────────────
AREA_UI = {
    "regulamento-interno": {
        "icono": "📋", "cls": "pci-cyan",
        "desc": "Normativa interna, regras de funcionamento e documentação oficial do centro.",
        "documentos": [
            {"titulo": "Regulamento Interno 2024/25", "tipo": "PDF",      "desc": "Regras de funcionamento da escola."},
            {"titulo": "Código de Conduta do Aluno",  "tipo": "Documento","desc": "Normas de comportamento e participação."},
            {"titulo": "Política de Privacidade",     "tipo": "Documento","desc": "Tratamento de dados pessoais."},
        ],
    },
    "projeto-educativo": {
        "icono": "📖", "cls": "pci-green",
        "desc": "Projeto educativo da Academia Profissional Prof. Albino de Matos.",
        "documentos": [
            {"titulo": "Projeto Educativo de Centro", "tipo": "PDF",      "desc": "Documento orientador do projeto educativo."},
            {"titulo": "Missão, Visão e Valores",     "tipo": "Documento","desc": "Princípios institucionais da academia."},
            {"titulo": "Plano de Melhoria",           "tipo": "Documento","desc": "Ações de melhoria pedagógica e organizacional."},
        ],
    },
    "plano-atividades": {
        "icono": "📅", "cls": "pci-orange",
        "desc": "Atividades, eventos, calendários e planeamento anual da escola.",
        "documentos": [
            {"titulo": "Plano Anual de Atividades",         "tipo": "PDF",       "desc": "Planeamento anual."},
            {"titulo": "Calendário Escolar",                "tipo": "Calendário","desc": "Datas relevantes do ano letivo."},
            {"titulo": "Calendário de Provas e Avaliações", "tipo": "Calendário","desc": "Organização das avaliações."},
        ],
    },
    "eqavet": {
        "icono": "🏅", "cls": "pci-blue",
        "desc": "Documentos de qualidade, indicadores, avaliação e melhoria contínua.",
        "documentos": [
            {"titulo": "Referencial EQAVET",          "tipo": "PDF",      "desc": "Sistema de garantia da qualidade."},
            {"titulo": "Indicadores de Qualidade",    "tipo": "Relatório","desc": "Indicadores pedagógicos e institucionais."},
            {"titulo": "Plano de Melhoria EQAVET",    "tipo": "Documento","desc": "Ações de melhoria e acompanhamento."},
            {"titulo": "Relatórios de Autoavaliação", "tipo": "Relatório","desc": "Evidências e avaliação interna."},
        ],
    },
    "erasmus": {
        "icono": "🇪🇺", "cls": "pci-gray",
        "desc": "Mobilidades Erasmus+: candidaturas, relatórios e difusão de resultados.",
        "documentos": [
            {"titulo": "Mobilidades de Alunos",       "tipo": "Documento", "desc": "Informação e candidaturas para alunos."},
            {"titulo": "Mobilidades de Pessoal",      "tipo": "Documento", "desc": "Informação para docentes e colaboradores."},
            {"titulo": "Relatórios de Mobilidade",    "tipo": "Relatório", "desc": "Relatórios e evidências."},
            {"titulo": "Difusão de Resultados",       "tipo": "Documento", "desc": "Projetos, resultados e impactos."},
            {"titulo": "Candidatura Online Erasmus+", "tipo": "Formulário","desc": "Formulário e prazos."},
            {"titulo": "Apoio ao Participante",       "tipo": "Documento", "desc": "Apoio antes, durante e após a mobilidade."},
        ],
    },
    "manual-aluno": {
        "icono": "🎒", "cls": "pci-red",
        "desc": "Informação de apoio aos alunos, regras, contactos e procedimentos.",
        "documentos": [
            {"titulo": "Manual do Aluno",                  "tipo": "PDF",     "desc": "Guia geral para alunos."},
            {"titulo": "Guia de Utilização da Plataforma", "tipo": "Tutorial","desc": "Como usar o campus virtual."},
            {"titulo": "Guia FCT",                         "tipo": "Documento","desc": "Formação em Contexto de Trabalho."},
            {"titulo": "Guia PAP",                         "tipo": "Documento","desc": "Prova de Aptidão Profissional."},
        ],
    },
    "manual-formador": {
        "icono": "👨‍🏫", "cls": "pci-green", "restrito": True,
        "desc": "Recursos internos para docentes, instrumentos e planificações.",
        "documentos": [
            {"titulo": "Manual do Formador",        "tipo": "PDF",    "desc": "Guia interno para docentes."},
            {"titulo": "Instrumentos de Avaliação", "tipo": "Modelo", "desc": "Modelos de grelhas e critérios."},
            {"titulo": "Planificações",             "tipo": "Modelo", "desc": "Modelos de planificação anual e modular."},
            {"titulo": "Rúbricas e Atas",           "tipo": "Documento","desc": "Documentação pedagógica."},
        ],
    },
    "biblioteca-digital": {
        "icono": "📚", "cls": "pci-cyan",
        "desc": "Recursos digitais, documentos de apoio e materiais de estudo.",
        "documentos": [
            {"titulo": "Catálogo de Recursos Digitais",  "tipo": "Link",       "desc": "Listagem de recursos."},
            {"titulo": "Repositório de Trabalhos PAP",   "tipo": "Repositório","desc": "Exemplos e evidências."},
            {"titulo": "Tutoriais e Vídeos de Apoio",    "tipo": "Vídeo",      "desc": "Materiais de apoio ao estudo."},
        ],
    },
    "centro-qualifica": {
        "icono": "🎓", "cls": "pci-orange",
        "desc": "Reconhecimento, validação e certificação de competências.",
        "documentos": [
            {"titulo": "O que é o Centro Qualifica",    "tipo": "Documento", "desc": "Informação geral."},
            {"titulo": "Processo RVCC",                 "tipo": "Documento", "desc": "Reconhecimento, Validação e Certificação."},
            {"titulo": "Candidatura ao Centro Qualifica","tipo": "Formulário","desc": "Pré-inscrição e contactos."},
        ],
    },
    "area-docente": {
        "icono": "🔒", "cls": "pci-gray", "restrito": True,
        "desc": "Planificações, instrumentos, atas, rúbricas e seguimento pedagógico.",
        "documentos": [
            {"titulo": "Planificações",                   "tipo": "Documento","desc": "Planificações anuais e modulares."},
            {"titulo": "Instrumentos de Avaliação",       "tipo": "Modelo",   "desc": "Testes, grelhas e critérios."},
            {"titulo": "Atas",                            "tipo": "Documento","desc": "Registo de reuniões."},
            {"titulo": "Rúbricas de Avaliação",           "tipo": "PDF",      "desc": "Escalas e indicadores."},
            {"titulo": "Seguimento Pedagógico",           "tipo": "Documento","desc": "Acompanhamento de alunos."},
            {"titulo": "Recursos Compartilhados",         "tipo": "Documento","desc": "Banco de materiais."},
        ],
    },
    # ── Centros Tecnológicos ──────────────────────────────────
    "centros-tecnologicos": {
        "icono": "🏭", "cls": "pci-blue",
        "desc": "Centros de referência tecnológica: CTE Informática e CTE Industrial.",
        "documentos": [
            {"titulo": "Apresentação dos CTEs",         "tipo": "Documento","desc": "Visão geral dos Centros Tecnológicos."},
            {"titulo": "Equipamentos e Infraestrutura", "tipo": "Documento","desc": "Inventário de laboratórios e equipamentos."},
            {"titulo": "Oferta Formativa dos CTEs",     "tipo": "PDF",      "desc": "Áreas de formação e competências."},
        ],
    },
    "cte-informatica": {
        "icono": "💻", "cls": "pci-cyan",
        "desc": "Programação, Inteligência Artificial, Robótica e Realidade Virtual.",
        "documentos": [
            {"titulo": "Guia de Competências CTE Informática",  "tipo": "PDF",      "desc": "Programação, IA, Robótica e RV."},
            {"titulo": "Infraestrutura e Laboratórios",          "tipo": "Documento","desc": "Equipamentos e software disponíveis."},
            {"titulo": "Percursos de Programação",               "tipo": "PDF",      "desc": "Python, Java, JavaScript e projetos reais."},
            {"titulo": "Especialização em IA",                   "tipo": "Documento","desc": "ML, Deep Learning, NLP."},
            {"titulo": "Robótica Educativa",                     "tipo": "Documento","desc": "Arduino, ROS, drones."},
            {"titulo": "Realidade Virtual e Aumentada",          "tipo": "Documento","desc": "Unity, Unreal Engine, WebVR."},
        ],
    },
    "cte-industrial": {
        "icono": "⚙️", "cls": "pci-orange",
        "desc": "CNC, CAD/CAM, Automatização Industrial e Indústria 5.0.",
        "documentos": [
            {"titulo": "Guia de Máquinas CNC",              "tipo": "PDF",      "desc": "Inventário e especificações."},
            {"titulo": "CAD/CAM — Software e Procedimentos","tipo": "Documento","desc": "AutoCAD, Fusion 360, Mastercam."},
            {"titulo": "Automatização Industrial",          "tipo": "Documento","desc": "PLCs, SCADA, programação industrial."},
            {"titulo": "Indústria 5.0 — IoT",               "tipo": "Documento","desc": "IoT, sensores e dados em tempo real."},
            {"titulo": "Segurança Industrial",              "tipo": "PDF",      "desc": "Normas, EPI e procedimentos."},
        ],
    },
    # ── EFA ───────────────────────────────────────────────────
    "efa": {
        "icono": "👨‍🎓", "cls": "pci-green",
        "desc": "Percursos EFA Escolar e Profissional para adultos.",
        "documentos": [
            {"titulo": "O que é EFA?",              "tipo": "Documento",  "desc": "Explicação geral dos percursos EFA."},
            {"titulo": "Destinatários e Requisitos","tipo": "Documento",  "desc": "Critérios de admissão."},
            {"titulo": "Estrutura dos Percursos",   "tipo": "PDF",        "desc": "Componentes, duração e certificações."},
            {"titulo": "Processo de Inscrição",     "tipo": "Formulário", "desc": "Como candidatar-se."},
        ],
    },
    "efa-escolar": {
        "icono": "📗", "cls": "pci-cyan",
        "desc": "Componente escolar dos percursos EFA.",
        "documentos": [
            {"titulo": "Guia da Componente Escolar","tipo": "PDF",      "desc": "Estrutura e avaliação."},
            {"titulo": "Português e Matemática",    "tipo": "Documento","desc": "Disciplinas nucleares."},
            {"titulo": "Cidadania e Desenvolvimento","tipo": "Documento","desc": "Participação cívica."},
        ],
    },
    "efa-profissional": {
        "icono": "🔧", "cls": "pci-orange",
        "desc": "Componente profissional dos percursos EFA.",
        "documentos": [
            {"titulo": "Guia da Componente Profissional",  "tipo": "PDF",      "desc": "Estrutura, FCT e avaliação."},
            {"titulo": "Áreas de Formação Disponíveis",    "tipo": "Documento","desc": "Cursos EFA em oferta."},
            {"titulo": "Formação em Contexto de Trabalho", "tipo": "Documento","desc": "FCT: procedimentos e empresas."},
        ],
    },
    # ── Formação Modular ──────────────────────────────────────
    "formacao-modular-certificada": {
        "icono": "🧩", "cls": "pci-blue",
        "desc": "Cursos modulares certificados para desenvolvimento de competências.",
        "documentos": [
            {"titulo": "O que é FMC?",                    "tipo": "Documento", "desc": "Modelo modular e certificação."},
            {"titulo": "Catálogo de Módulos",             "tipo": "PDF",       "desc": "Módulos disponíveis por área."},
            {"titulo": "Sistema de Créditos",             "tipo": "Documento", "desc": "Acumulação e progressão."},
            {"titulo": "Inscrição em Módulos",            "tipo": "Formulário","desc": "Como inscrever-se."},
        ],
    },
}

LINKS_UTILES = [
    {"label": "ANQEP",                            "url": "https://www.anqep.gov.pt"},
    {"label": "Catálogo Nacional de Qualificações","url": "https://www.catalogo.anqep.gov.pt"},
    {"label": "IEFP",                             "url": "https://www.iefp.pt"},
    {"label": "Erasmus+ Portugal",                "url": "https://www.erasmusmais.pt"},
]


# ── helpers ───────────────────────────────────────────────────

def _get_ui(slug):
    return AREA_UI.get(slug, {
        "icono": "📘", "cls": "pci-cyan",
        "desc": "Área institucional da Academia Profissional Prof. Albino de Matos.",
        "documentos": [],
    })


def _url_action_label(url, tipo=None):
    """Etiqueta de ação para botão de documento baseada na extensão da URL."""
    if not url:
        return "Sem ficheiro"
    ul = url.lower().split("?")[0]
    if ul.endswith(".pdf"):                              return "Abrir PDF"
    if ul.endswith((".doc", ".docx")):                  return "Abrir documento"
    if ul.endswith((".xls", ".xlsx")):                  return "Abrir folha de cálculo"
    if ul.endswith((".ppt", ".pptx")):                  return "Abrir apresentação"
    if ul.endswith((".jpg", ".jpeg", ".png", ".webp")): return "Ver imagem"
    if ul.endswith((".mp4", ".avi", ".mov", ".webm")):  return "Ver vídeo"
    if ul.startswith("http"):                           return "Abrir ligação"
    if ul.startswith("/static/uploads/"):
        ext = ul.rsplit(".", 1)[-1] if "." in ul else ""
        if ext == "pdf":          return "Abrir PDF"
        if ext in ("doc","docx"): return "Abrir documento"
        return "Abrir ficheiro"
    return "Abrir ficheiro"


def _normalize_docs(area_slug):
    """Docs da BD; fallback para AREA_UI se a BD não tiver."""
    docs_db = get_documentos_by_area(area_slug)
    if docs_db:
        return [
            {
                "titulo": d.get("titulo", ""),
                "tipo":   d.get("tipo", "Documento"),
                "desc":   d.get("descripcion") or d.get("desc") or "",
                "url":    d.get("url"),
                "_action_label": _url_action_label(d.get("url"), d.get("tipo")),
            }
            for d in docs_db
        ]
    docs = _get_ui(area_slug).get("documentos", [])
    return [{**d, "_action_label": _url_action_label(d.get("url"), d.get("tipo"))}
            for d in docs]


def _area_to_view(area):
    slug     = area["slug"]
    ui       = _get_ui(slug)
    titulo   = area.get("titulo") or slug
    descr    = area.get("descricao") or area.get("descripcion") or ui.get("desc", "")
    conteudo = area.get("conteudo") or ""
    return {
        "id": area.get("id"), "slug": slug,
        "titulo": titulo, "nombre": titulo,
        "icono":  area.get("icono") or ui.get("icono", "📘"),
        "cls":    ui.get("cls", "pci-cyan"),
        "desc": descr, "descripcion": descr,
        "intro":    conteudo or descr,
        "conteudo": conteudo,
        "restrito":    area.get("restringido", False) or ui.get("restrito", False),
        "restringido": area.get("restringido", False) or ui.get("restrito", False),
        "documentos": _normalize_docs(slug),
    }


def _fallback_area(slug):
    ui    = _get_ui(slug)
    docs  = [{**d, "_action_label": _url_action_label(d.get("url"), d.get("tipo"))}
             for d in ui.get("documentos", [])]
    titulo = slug.replace("-", " ").title()
    return {
        "id": None, "slug": slug,
        "titulo": titulo, "nombre": titulo,
        "icono": ui.get("icono", "📘"), "cls": ui.get("cls", "pci-cyan"),
        "desc": ui.get("desc", ""), "descripcion": ui.get("desc", ""),
        "intro": ui.get("desc", ""), "conteudo": "",
        "restrito": ui.get("restrito", False),
        "restringido": ui.get("restrito", False),
        "documentos": docs,
    }


def _build_portal_cards():
    areas_db      = get_areas_moodle()
    areas_by_slug = {a["slug"]: a for a in areas_db}
    cards = []
    for slug in PORTAL_ORDER:
        area_db = areas_by_slug.get(slug)
        area    = _area_to_view(area_db) if area_db else _fallback_area(slug)
        cards.append({
            "slug": slug, "titulo": area["titulo"],
            "icono": area["icono"], "cls": area["cls"],
            "desc": area["desc"],  "restrito": area["restrito"],
        })
    return cards


def _build_context(area_slug=None):
    usuario = get_current_user()
    centro  = get_centro()
    avisos  = get_notices()
    for a in avisos:
        a["_fecha"] = format_date(a["fecha"])

    area_activa = None
    if area_slug:
        area_db = get_area_by_slug(area_slug)
        area_activa = _area_to_view(area_db) if area_db else _fallback_area(area_slug)

    return {
        "usuario": usuario, "centro": centro,
        "portal_cards": _build_portal_cards(),
        "links_utiles": LINKS_UTILES,
        "avisos": avisos,
        "area_activa": area_activa,
        "active_area_slug": area_slug,
    }


def _can_access(area_slug):
    """True se o utilizador actual pode aceder ao slug."""
    required = AREAS_RESTRITAS.get(area_slug)
    if not required:
        return True
    if session.get("admin_ok") is True:
        return True
    return any(r in session.get("usuario_roles", []) for r in required)


# ── rotas ─────────────────────────────────────────────────────

@portal_bp.route("/portal")
def portal():
    area = request.args.get("area")
    if area:
        area = AREA_ALIASES.get(area, area)
        return redirect(url_for("portal.portal_area", area_slug=area))
    return render_template("portal.html", **_build_context())


@portal_bp.route("/portal/<area_slug>")
def portal_area(area_slug):
    area_slug = AREA_ALIASES.get(area_slug, area_slug)
    area_db   = get_area_by_slug(area_slug)

    # 404 solo si no está en BD ni en AREA_UI (slug completamente desconocido)
    if not area_db and area_slug not in AREA_UI:
        return render_template("404.html", usuario=get_current_user()), 404

    if not _can_access(area_slug):
        flash("Esta área é de acesso restrito. Inicia sessão como docente ou administrador.", "warning")
        return redirect(url_for("auth.login", next=f"/portal/{area_slug}"))

    return render_template("portal.html", **_build_context(area_slug))

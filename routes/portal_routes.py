"""
Blueprint: Portal institucional.
Rutas: /portal y /portal/<area_slug>
"""

from flask import Blueprint, render_template, request, redirect, url_for

from services.data_service import (
    get_current_user,
    get_notices,
    get_centro,
    format_date,
    get_areas_moodle,
    get_area_by_slug,
    get_documentos_by_area,
)

portal_bp = Blueprint("portal", __name__)


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
}


PORTAL_ORDER = [
    "regulamento-interno",
    "projeto-educativo",
    "plano-atividades",
    "eqavet",
    "erasmus",
    "manual-aluno",
    "manual-formador",
    "biblioteca-digital",
    "centro-qualifica",
    "area-docente",
]


AREA_UI = {
    "regulamento-interno": {
        "icono": "📋",
        "cls": "pci-cyan",
        "desc": "Normativa interna, regras de funcionamento e documentação oficial do centro.",
        "documentos": [
            {"titulo": "Regulamento Interno 2024/25", "tipo": "PDF", "desc": "Documento principal com regras de funcionamento da escola."},
            {"titulo": "Código de Conduta do Aluno", "tipo": "Documento", "desc": "Normas de comportamento, assiduidade e participação."},
            {"titulo": "Política de Privacidade", "tipo": "Documento", "desc": "Tratamento de dados pessoais e privacidade na plataforma."},
        ],
    },
    "projeto-educativo": {
        "icono": "📖",
        "cls": "pci-green",
        "desc": "Projeto educativo da Academia Profissional Prof. Albino de Matos.",
        "documentos": [
            {"titulo": "Projeto Educativo de Centro", "tipo": "PDF", "desc": "Documento orientador do projeto educativo."},
            {"titulo": "Missão, Visão e Valores", "tipo": "Documento", "desc": "Princípios institucionais da academia."},
            {"titulo": "Plano de Melhoria", "tipo": "Documento", "desc": "Ações de melhoria pedagógica e organizacional."},
        ],
    },
    "plano-atividades": {
        "icono": "📅",
        "cls": "pci-orange",
        "desc": "Atividades, eventos, calendários e planeamento anual da escola.",
        "documentos": [
            {"titulo": "Plano Anual de Atividades", "tipo": "PDF", "desc": "Planeamento anual das atividades do centro."},
            {"titulo": "Calendário Escolar", "tipo": "Calendário", "desc": "Datas relevantes do ano letivo."},
            {"titulo": "Calendário de Provas e Avaliações", "tipo": "Calendário", "desc": "Organização de momentos de avaliação."},
        ],
    },
    "eqavet": {
        "icono": "🏅",
        "cls": "pci-blue",
        "desc": "Documentos de qualidade, indicadores, avaliação e melhoria contínua.",
        "documentos": [
            {"titulo": "Referencial EQAVET", "tipo": "PDF", "desc": "Documentação base do sistema de garantia da qualidade."},
            {"titulo": "Indicadores de Qualidade", "tipo": "Relatório", "desc": "Indicadores pedagógicos e institucionais."},
            {"titulo": "Plano de Melhoria EQAVET", "tipo": "Documento", "desc": "Ações de melhoria e acompanhamento."},
            {"titulo": "Relatórios de Autoavaliação", "tipo": "Relatório", "desc": "Evidências e avaliação interna."},
        ],
    },
    "erasmus": {
        "icono": "🇪🇺",
        "cls": "pci-gray",
        "desc": "Mobilidades, candidaturas, relatórios e divulgação de resultados.",
        "documentos": [
            {"titulo": "Mobilidades de Alunos", "tipo": "Documento", "desc": "Informação e candidaturas para alunos."},
            {"titulo": "Mobilidades de Pessoal", "tipo": "Documento", "desc": "Informação para docentes e colaboradores."},
            {"titulo": "Relatórios de Mobilidade", "tipo": "Relatório", "desc": "Relatórios e evidências de mobilidade."},
            {"titulo": "Difusão de Resultados", "tipo": "Documento", "desc": "Divulgação de projetos, resultados e impactos."},
        ],
    },
    "manual-aluno": {
        "icono": "🎒",
        "cls": "pci-red",
        "desc": "Informação de apoio aos alunos, regras, contactos e procedimentos.",
        "documentos": [
            {"titulo": "Manual do Aluno", "tipo": "PDF", "desc": "Guia geral para alunos."},
            {"titulo": "Guia de Utilização da Plataforma", "tipo": "Tutorial", "desc": "Como usar o campus virtual."},
            {"titulo": "Guia FCT", "tipo": "Documento", "desc": "Formação em Contexto de Trabalho."},
            {"titulo": "Guia PAP", "tipo": "Documento", "desc": "Prova de Aptidão Profissional."},
        ],
    },
    "manual-formador": {
        "icono": "👨‍🏫",
        "cls": "pci-green",
        "desc": "Recursos internos para docentes, instrumentos de avaliação e planificações.",
        "restrito": True,
        "documentos": [
            {"titulo": "Manual do Formador", "tipo": "PDF", "desc": "Guia interno para docentes/formadores."},
            {"titulo": "Instrumentos de Avaliação", "tipo": "Modelo", "desc": "Modelos de grelhas e critérios."},
            {"titulo": "Planificações", "tipo": "Modelo", "desc": "Modelos de planificação anual e modular."},
            {"titulo": "Rúbricas e Atas", "tipo": "Documento", "desc": "Documentação de acompanhamento pedagógico."},
        ],
    },
    "biblioteca-digital": {
        "icono": "📚",
        "cls": "pci-cyan",
        "desc": "Recursos digitais, documentos de apoio e materiais de estudo.",
        "documentos": [
            {"titulo": "Catálogo de Recursos Digitais", "tipo": "Link", "desc": "Listagem de recursos disponíveis."},
            {"titulo": "Repositório de Trabalhos PAP", "tipo": "Repositório", "desc": "Exemplos e evidências de projetos."},
            {"titulo": "Tutoriais e Vídeos de Apoio", "tipo": "Vídeo", "desc": "Materiais de apoio ao estudo."},
        ],
    },
    "centro-qualifica": {
        "icono": "🎓",
        "cls": "pci-orange",
        "desc": "Reconhecimento, validação e certificação de competências.",
        "documentos": [
            {"titulo": "O que é o Centro Qualifica", "tipo": "Documento", "desc": "Informação geral sobre o serviço."},
            {"titulo": "Processo RVCC", "tipo": "Documento", "desc": "Reconhecimento, Validação e Certificação de Competências."},
            {"titulo": "Candidatura ao Centro Qualifica", "tipo": "Formulário", "desc": "Pré-inscrição e contactos."},
        ],
    },
    "area-docente": {
        "icono": "🔒",
        "cls": "pci-gray",
        "desc": "Planificações, instrumentos, atas, rúbricas e seguimento pedagógico.",
        "restrito": True,
        "documentos": [
            {"titulo": "Planificações", "tipo": "Documento", "desc": "Planificações anuais e modulares."},
            {"titulo": "Instrumentos de Avaliação", "tipo": "Modelo", "desc": "Testes, grelhas, critérios e rubricas."},
            {"titulo": "Atas", "tipo": "Documento", "desc": "Registo de reuniões e acompanhamento."},
            {"titulo": "Seguimento Pedagógico", "tipo": "Documento", "desc": "Acompanhamento de alunos e turmas."},
        ],
    },
}


LINKS_UTILES = [
    {"label": "ANQEP", "url": "https://www.anqep.gov.pt"},
    {"label": "Catálogo Nacional de Qualificações", "url": "https://www.catalogo.anqep.gov.pt"},
    {"label": "IEFP", "url": "https://www.iefp.pt"},
    {"label": "Erasmus+ Portugal", "url": "https://www.erasmusmais.pt"},
]


def _get_ui(slug):
    return AREA_UI.get(slug, {
        "icono": "📘",
        "cls": "pci-cyan",
        "desc": "Área institucional da Academia Profissional Prof. Albino de Matos.",
        "documentos": [],
    })


def _normalizar_documentos(area_slug):
    """
    Intenta cargar documentos desde BD.
    Si no hay tabla/documentos todavía, usa documentos visuales de fallback.
    """
    documentos_db = get_documentos_by_area(area_slug)

    if documentos_db:
        return [
            {
                "titulo": d.get("titulo", ""),
                "tipo": d.get("tipo", "Documento"),
                "desc": d.get("descripcion") or d.get("desc") or "",
                "url": d.get("url"),
            }
            for d in documentos_db
        ]

    return _get_ui(area_slug).get("documentos", [])


def _area_to_view(area):
    """
    Convierte un área de MySQL al formato que espera portal.html.
    """
    slug = area["slug"]
    ui = _get_ui(slug)

    titulo = area.get("titulo") or area.get("nombre") or slug
    descripcion = area.get("descripcion") or ui.get("desc", "")
    conteudo = area.get("conteudo") or ""

    return {
        "id": area.get("id"),
        "slug": slug,
        "titulo": titulo,
        "nombre": titulo,
        "icono": area.get("icono") or ui.get("icono", "📘"),
        "cls": ui.get("cls", "pci-cyan"),
        "desc": descripcion,
        "descripcion": descripcion,

        # Esta es la clave: ahora la intro sale del campo conteudo de MySQL.
        "intro": conteudo or descripcion,
        "conteudo": conteudo,

        "restrito": area.get("restringido", False) or ui.get("restrito", False),
        "restringido": area.get("restringido", False) or ui.get("restrito", False),
        "documentos": _normalizar_documentos(slug),
    }


def _fallback_area(slug):
    """
    Fallback por si no existe el área en MySQL.
    """
    ui = _get_ui(slug)

    titulo = slug.replace("-", " ").title()

    return {
        "id": None,
        "slug": slug,
        "titulo": titulo,
        "nombre": titulo,
        "icono": ui.get("icono", "📘"),
        "cls": ui.get("cls", "pci-cyan"),
        "desc": ui.get("desc", ""),
        "descripcion": ui.get("desc", ""),
        "intro": ui.get("desc", ""),
        "conteudo": "",
        "restrito": ui.get("restrito", False),
        "restringido": ui.get("restrito", False),
        "documentos": ui.get("documentos", []),
    }


def _build_portal_cards():
    """
    Construye las tarjetas del portal desde MySQL.
    Usa AREA_UI solo para iconos, colores y documentos visuales.
    """
    areas_db = get_areas_moodle()
    areas_by_slug = {a["slug"]: a for a in areas_db}

    cards = []

    for slug in PORTAL_ORDER:
        area_db = areas_by_slug.get(slug)

        if area_db:
            area = _area_to_view(area_db)
        else:
            area = _fallback_area(slug)

        cards.append({
            "slug": slug,
            "titulo": area["titulo"],
            "icono": area["icono"],
            "cls": area["cls"],
            "desc": area["desc"],
            "restrito": area["restrito"],
        })

    return cards


def _build_context(area_slug=None):
    usuario = get_current_user()
    centro = get_centro()
    avisos = get_notices()

    for aviso in avisos:
        aviso["_fecha"] = format_date(aviso["fecha"])

    area_activa = None

    if area_slug:
        area_db = get_area_by_slug(area_slug)

        if area_db:
            area_activa = _area_to_view(area_db)
        else:
            area_activa = None

    return {
        "usuario": usuario,
        "centro": centro,
        "portal_cards": _build_portal_cards(),
        "links_utiles": LINKS_UTILES,
        "avisos": avisos,
        "area_activa": area_activa,
        "active_area_slug": area_slug,
    }


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

    area_db = get_area_by_slug(area_slug)

    if not area_db:
        return render_template("404.html", usuario=get_current_user()), 404

    return render_template("portal.html", **_build_context(area_slug))
"""
Blueprint: Portal institucional.
Rutas: /portal y /portal/<area_slug>
"""

from flask import Blueprint, render_template, request, redirect, url_for
from services.data_service import get_current_user, get_notices, get_centro, format_date

portal_bp = Blueprint('portal', __name__)

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

PORTAL_AREAS = {
    "regulamento-interno": {
        "titulo": "Regulamento Interno",
        "icono": "📋",
        "cls": "pci-cyan",
        "desc": "Normativa interna, regras de funcionamento e documentação oficial do centro.",
        "intro": "Espaço para consulta das normas internas, direitos, deveres, procedimentos e documentos orientadores da Academia Profissional Prof. Albino de Matos.",
        "documentos": [
            {"titulo": "Regulamento Interno 2024/25", "tipo": "PDF", "desc": "Documento principal com regras de funcionamento da escola."},
            {"titulo": "Código de Conduta do Aluno", "tipo": "Documento", "desc": "Normas de comportamento, assiduidade e participação."},
            {"titulo": "Política de Privacidade", "tipo": "Documento", "desc": "Tratamento de dados pessoais e privacidade na plataforma."},
        ],
    },
    "projeto-educativo": {
        "titulo": "Projeto Educativo",
        "icono": "📖",
        "cls": "pci-green",
        "desc": "Projeto educativo da Academia Profissional Prof. Albino de Matos.",
        "intro": "Área dedicada à missão, visão, valores, objetivos pedagógicos e linhas estratégicas do projeto educativo.",
        "documentos": [
            {"titulo": "Projeto Educativo de Centro", "tipo": "PDF", "desc": "Documento orientador do projeto educativo."},
            {"titulo": "Missão, Visão e Valores", "tipo": "Documento", "desc": "Princípios institucionais da academia."},
            {"titulo": "Plano de Melhoria", "tipo": "Documento", "desc": "Ações de melhoria pedagógica e organizacional."},
        ],
    },
    "plano-atividades": {
        "titulo": "Plano Anual de Atividades",
        "icono": "📅",
        "cls": "pci-orange",
        "desc": "Atividades, eventos, calendários e planeamento anual da escola.",
        "intro": "Calendário de atividades escolares, eventos, reuniões, sessões de orientação, provas e iniciativas pedagógicas.",
        "documentos": [
            {"titulo": "Plano Anual de Atividades", "tipo": "PDF", "desc": "Planeamento anual das atividades do centro."},
            {"titulo": "Calendário Escolar", "tipo": "Calendário", "desc": "Datas relevantes do ano letivo."},
            {"titulo": "Calendário de Provas e Avaliações", "tipo": "Calendário", "desc": "Organização de momentos de avaliação."},
        ],
    },
    "eqavet": {
        "titulo": "EQAVET",
        "icono": "🏅",
        "cls": "pci-blue",
        "desc": "Documentos de qualidade, indicadores, avaliação e melhoria contínua.",
        "intro": "Área de qualidade alinhada com o quadro EQAVET: indicadores, autoavaliação, melhoria contínua e evidências do sistema de garantia da qualidade.",
        "documentos": [
            {"titulo": "Referencial EQAVET", "tipo": "PDF", "desc": "Documentação base do sistema de garantia da qualidade."},
            {"titulo": "Indicadores de Qualidade", "tipo": "Relatório", "desc": "Indicadores pedagógicos e institucionais."},
            {"titulo": "Plano de Melhoria EQAVET", "tipo": "Documento", "desc": "Ações de melhoria e acompanhamento."},
            {"titulo": "Relatórios de Autoavaliação", "tipo": "Relatório", "desc": "Evidências e avaliação interna."},
        ],
    },
    "erasmus": {
        "titulo": "Erasmus+",
        "icono": "🇪🇺",
        "cls": "pci-gray",
        "desc": "Mobilidades, candidaturas, relatórios e divulgação de resultados.",
        "intro": "Espaço para projetos Erasmus+, mobilidades internacionais, documentação de candidatura, relatórios e disseminação de resultados.",
        "documentos": [
            {"titulo": "Mobilidades de Alunos", "tipo": "Documento", "desc": "Informação e candidaturas para alunos."},
            {"titulo": "Mobilidades de Pessoal", "tipo": "Documento", "desc": "Informação para docentes e colaboradores."},
            {"titulo": "Relatórios de Mobilidade", "tipo": "Relatório", "desc": "Relatórios e evidências de mobilidade."},
            {"titulo": "Difusão de Resultados", "tipo": "Documento", "desc": "Divulgação de projetos, resultados e impactos."},
        ],
    },
    "manual-aluno": {
        "titulo": "Manual do Aluno",
        "icono": "🎒",
        "cls": "pci-red",
        "desc": "Informação de apoio aos alunos, regras, contactos e procedimentos.",
        "intro": "Guia para os alunos com informação sobre funcionamento da plataforma, avaliação, FCT, PAP, contactos e procedimentos administrativos.",
        "documentos": [
            {"titulo": "Manual do Aluno", "tipo": "PDF", "desc": "Guia geral para alunos."},
            {"titulo": "Guia de Utilização da Plataforma", "tipo": "Tutorial", "desc": "Como usar o campus virtual."},
            {"titulo": "Guia FCT", "tipo": "Documento", "desc": "Formação em Contexto de Trabalho."},
            {"titulo": "Guia PAP", "tipo": "Documento", "desc": "Prova de Aptidão Profissional."},
        ],
    },
    "manual-formador": {
        "titulo": "Manual do Formador",
        "icono": "👨‍🏫",
        "cls": "pci-green",
        "desc": "Recursos internos para docentes, instrumentos de avaliação e planificações.",
        "intro": "Área de apoio ao corpo docente com planificações, instrumentos de avaliação, rubricas, atas e recursos partilhados.",
        "restrito": True,
        "documentos": [
            {"titulo": "Manual do Formador", "tipo": "PDF", "desc": "Guia interno para docentes/formadores."},
            {"titulo": "Instrumentos de Avaliação", "tipo": "Modelo", "desc": "Modelos de grelhas e critérios."},
            {"titulo": "Planificações", "tipo": "Modelo", "desc": "Modelos de planificação anual e modular."},
            {"titulo": "Rúbricas e Atas", "tipo": "Documento", "desc": "Documentação de acompanhamento pedagógico."},
        ],
    },
    "biblioteca-digital": {
        "titulo": "Biblioteca Digital",
        "icono": "📚",
        "cls": "pci-cyan",
        "desc": "Recursos digitais, documentos de apoio e materiais de estudo.",
        "intro": "Repositório de recursos pedagógicos, materiais de estudo, apresentações, manuais, ligações úteis e trabalhos de referência.",
        "documentos": [
            {"titulo": "Catálogo de Recursos Digitais", "tipo": "Link", "desc": "Listagem de recursos disponíveis."},
            {"titulo": "Repositório de Trabalhos PAP", "tipo": "Repositório", "desc": "Exemplos e evidências de projetos."},
            {"titulo": "Tutoriais e Vídeos de Apoio", "tipo": "Vídeo", "desc": "Materiais de apoio ao estudo."},
        ],
    },
    "centro-qualifica": {
        "titulo": "Centro Qualifica",
        "icono": "🎓",
        "cls": "pci-orange",
        "desc": "Reconhecimento, validação e certificação de competências.",
        "intro": "Informação sobre processos de reconhecimento, validação e certificação de competências, candidaturas e acompanhamento de adultos.",
        "documentos": [
            {"titulo": "O que é o Centro Qualifica", "tipo": "Documento", "desc": "Informação geral sobre o serviço."},
            {"titulo": "Processo RVCC", "tipo": "Documento", "desc": "Reconhecimento, Validação e Certificação de Competências."},
            {"titulo": "Candidatura ao Centro Qualifica", "tipo": "Formulário", "desc": "Pré-inscrição e contactos."},
        ],
    },
    "area-docente": {
        "titulo": "Área Docente",
        "icono": "🔒",
        "cls": "pci-gray",
        "desc": "Planificações, instrumentos, atas, rúbricas e seguimento pedagógico.",
        "intro": "Área reservada para docentes/formadores. De momento está preparada visualmente; será protegida por roles quando o login estiver implementado.",
        "restrito": True,
        "documentos": [
            {"titulo": "Planificações", "tipo": "Documento", "desc": "Planificações anuais e modulares."},
            {"titulo": "Instrumentos de Avaliação", "tipo": "Modelo", "desc": "Testes, grelhas, critérios e rubricas."},
            {"titulo": "Atas", "tipo": "Documento", "desc": "Registo de reuniões e acompanhamento."},
            {"titulo": "Seguimento Pedagógico", "tipo": "Documento", "desc": "Acompanhamento de alunos e turmas."},
        ],
    },
}

PORTAL_ORDER = [
    "regulamento-interno", "projeto-educativo", "plano-atividades", "eqavet", "erasmus",
    "manual-aluno", "manual-formador", "biblioteca-digital", "centro-qualifica",
]

LINKS_UTILES = [
    {"label": "ANQEP", "url": "https://www.anqep.gov.pt"},
    {"label": "Catálogo Nacional de Qualificações", "url": "https://www.catalogo.anqep.gov.pt"},
    {"label": "IEFP", "url": "https://www.iefp.pt"},
    {"label": "Erasmus+ Portugal", "url": "https://www.erasmusmais.pt"},
]


def _build_context(area_slug=None):
    usuario = get_current_user()
    centro = get_centro()
    avisos = get_notices()

    for a in avisos:
        a['_fecha'] = format_date(a['fecha'])

    portal_cards = []
    for slug in PORTAL_ORDER:
        area = PORTAL_AREAS[slug]
        portal_cards.append({
            "slug": slug,
            "titulo": area["titulo"],
            "icono": area["icono"],
            "cls": area["cls"],
            "desc": area["desc"],
            "restrito": area.get("restrito", False),
        })

    area_activa = PORTAL_AREAS.get(area_slug) if area_slug else None
    if area_activa:
        area_activa = dict(area_activa)
        area_activa["slug"] = area_slug

    return {
        "usuario": usuario,
        "centro": centro,
        "portal_cards": portal_cards,
        "links_utiles": LINKS_UTILES,
        "avisos": avisos,
        "area_activa": area_activa,
        "active_area_slug": area_slug,
    }


@portal_bp.route('/portal')
def portal():
    area = request.args.get('area')
    if area:
        area = AREA_ALIASES.get(area, area)
        return redirect(url_for('portal.portal_area', area_slug=area))

    return render_template('portal.html', **_build_context())


@portal_bp.route('/portal/<area_slug>')
def portal_area(area_slug):
    area_slug = AREA_ALIASES.get(area_slug, area_slug)
    if area_slug not in PORTAL_AREAS:
        return render_template('404.html', usuario=get_current_user()), 404

    return render_template('portal.html', **_build_context(area_slug))

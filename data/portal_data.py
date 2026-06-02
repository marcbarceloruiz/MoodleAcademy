"""Datos estáticos del portal institucional APPAM.

Se mantienen fuera del blueprint para que las rutas no estén saturadas de
contenido. Cuando el portal pase a BD, este archivo será fácil de sustituir.
"""

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
        "cls": "pci-blue",
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
        "cls": "pci-blue",
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
        "cls": "pci-blue",
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
        "cls": "pci-blue",
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
        "cls": "pci-blue",
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
        "cls": "pci-blue",
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
    "regulamento-interno",
    "projeto-educativo",
    "plano-atividades",
    "eqavet",
    "erasmus",
    "manual-aluno",
    "manual-formador",
    "biblioteca-digital",
    "centro-qualifica",
]

LINKS_UTILES = [
    {"label": "ANQEP", "url": "https://www.anqep.gov.pt"},
    {"label": "Catálogo Nacional de Qualificações", "url": "https://www.catalogo.anqep.gov.pt"},
    {"label": "IEFP", "url": "https://www.iefp.pt"},
    {"label": "Erasmus+ Portugal", "url": "https://www.erasmusmais.pt"},
]


def normalize_area_slug(slug):
    """Acepta slugs antiguos/españoles y devuelve el slug oficial."""
    return AREA_ALIASES.get(slug, slug)


def get_portal_area(slug):
    """Devuelve una copia del área para evitar modificar el diccionario base."""
    normalized = normalize_area_slug(slug)
    area = PORTAL_AREAS.get(normalized)
    if not area:
        return None
    data = dict(area)
    data["slug"] = normalized
    return data


def get_portal_cards():
    return [
        {
            "slug": slug,
            "titulo": PORTAL_AREAS[slug]["titulo"],
            "icono": PORTAL_AREAS[slug]["icono"],
            "cls": PORTAL_AREAS[slug]["cls"],
            "desc": PORTAL_AREAS[slug]["desc"],
            "restrito": PORTAL_AREAS[slug].get("restrito", False),
        }
        for slug in PORTAL_ORDER
    ]

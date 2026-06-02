"""
Seed inicial seguro para APPAM / Escola Profissional Vértice.
Ejecutar desde la raíz del proyecto:

    python seed.py

No elimina datos existentes. Inserta o actualiza datos base si no existen.
"""
from app import create_app
from extensions import db
from models.centro import Centro
from models.area_moodle import AreaMoodle, DocumentoInstitucional
from models.ciclo_formativo import CicloFormativo, AnoCurso, Disciplina


NOME_OFICIAL = "Academia Profissional Prof. Albino de Matos - Escola Profissional Vértice"
NOME_CURTO = "Escola Profissional Vértice"


def ensure_centro():
    centro = Centro.query.first()
    if not centro:
        centro = Centro()
        db.session.add(centro)
    centro.nome_oficial = NOME_OFICIAL
    centro.nome_curto = NOME_CURTO
    centro.cidade = "Paços de Ferreira"
    centro.pais = "Portugal"
    db.session.commit()
    print("Centro comprobado")


def ensure_areas():
    areas = [
        ("regulamento-interno", "Regulamento Interno", "📋", "institucional", "Normativa interna, regras de funcionamento e documentação oficial do centro."),
        ("projeto-educativo", "Projeto Educativo", "📖", "institucional", "Projeto educativo da Academia Profissional Prof. Albino de Matos."),
        ("plano-atividades", "Plano Anual de Atividades", "📅", "institucional", "Atividades, eventos, calendários e planeamento anual da escola."),
        ("eqavet", "EQAVET", "🏅", "institucional", "Documentos de qualidade, indicadores, avaliação e melhoria contínua."),
        ("erasmus", "Erasmus+", "🇪🇺", "erasmus", "Mobilidades, candidaturas, relatórios e divulgação de resultados."),
        ("manual-aluno", "Manual do Aluno", "🎒", "institucional", "Informação de apoio aos alunos, regras, contactos e procedimentos."),
        ("manual-formador", "Manual do Formador", "👨‍🏫", "docente", "Recursos internos para docentes, instrumentos de avaliação e planificações."),
        ("biblioteca-digital", "Biblioteca Digital", "📚", "institucional", "Recursos digitais, documentos de apoio e materiais de estudo."),
        ("centro-qualifica", "Centro Qualifica", "🎓", "institucional", "Reconhecimento, validação e certificação de competências."),
        ("area-docente", "Área Docente", "🔒", "docente", "Planificações, instrumentos, atas, rúbricas e seguimento pedagógico."),
    ]
    aliases_to_remove = ["reglamento", "proyecto-educativo", "plan-actividades", "manual-alumno", "biblioteca"]
    for old_slug in aliases_to_remove:
        old = AreaMoodle.query.filter_by(slug=old_slug).first()
        if old:
            old.visible = False

    for orden, (slug, nombre, icono, tipo, descripcion) in enumerate(areas, start=1):
        area = AreaMoodle.query.filter_by(slug=slug).first()
        if not area:
            area = AreaMoodle(slug=slug)
            db.session.add(area)
        area.nombre = nombre
        area.icono = icono
        area.tipo = tipo
        area.descripcion = descripcion
        area.orden = orden
        area.visible = True
        area.restringido = slug in {"area-docente", "manual-formador"}
    db.session.commit()
    print("Áreas Moodle comprobadas")

    docs = {
        "regulamento-interno": [
            "Regulamento Interno 2024/25", "Código de Conduta do Aluno", "Política de Privacidade"
        ],
        "projeto-educativo": ["Projeto Educativo de Centro", "Missão, Visão e Valores", "Plano de Melhoria"],
        "plano-atividades": ["Plano Anual de Atividades", "Calendário Escolar", "Calendário de Provas e Avaliações"],
        "eqavet": ["Referencial EQAVET", "Indicadores de Qualidade", "Plano de Melhoria EQAVET", "Relatórios de Autoavaliação"],
        "erasmus": ["Mobilidades de Alunos", "Mobilidades de Pessoal", "Relatórios de Mobilidade", "Difusão de Resultados"],
        "manual-aluno": ["Manual do Aluno", "Guia de Utilização da Plataforma", "Guia FCT", "Guia PAP"],
        "manual-formador": ["Manual do Formador", "Instrumentos de Avaliação", "Planificações", "Rúbricas e Atas"],
        "biblioteca-digital": ["Catálogo de Recursos Digitais", "Repositório de Trabalhos PAP", "Tutoriais e Vídeos de Apoio"],
        "centro-qualifica": ["O que é o Centro Qualifica", "Processo RVCC", "Candidatura ao Centro Qualifica"],
        "area-docente": ["Planificações", "Instrumentos de Avaliação", "Atas", "Rúbricas", "Seguimento Pedagógico"],
    }
    for slug, titulos in docs.items():
        area = AreaMoodle.query.filter_by(slug=slug).first()
        if not area:
            continue
        for i, titulo in enumerate(titulos, start=1):
            doc = DocumentoInstitucional.query.filter_by(area_id=area.id, titulo=titulo).first()
            if not doc:
                db.session.add(DocumentoInstitucional(area_id=area.id, titulo=titulo, tipo="documento", orden=i))
    db.session.commit()
    print("Documentos institucionales comprobados")


def add_or_update_ciclo(codigo, nombre, area, nivel, duracion, descripcion, orden):
    ciclo = CicloFormativo.query.filter_by(codigo=codigo).first()
    if not ciclo:
        ciclo = CicloFormativo(codigo=codigo)
        db.session.add(ciclo)
    ciclo.nombre = nombre
    ciclo.area = area
    ciclo.nivel = nivel
    ciclo.duracion = duracion
    ciclo.descripcion = descripcion
    ciclo.activo = True
    ciclo.orden = orden
    db.session.flush()

    # Crea estructura de 3 años solo si todavía no existe. No borra cambios del usuario.
    if not ciclo.anos:
        base = {
            1: ("10º", ["Português", "Inglês", "Área de Integração", "Educação Física", "Formação Técnica I"]),
            2: ("11º", ["Português", "Inglês Técnico", "Área de Integração", "Formação Técnica II", "Projeto Técnico"]),
            3: ("12º", ["Formação Técnica III", "FCT — Formação em Contexto de Trabalho", "PAP — Prova de Aptidão Profissional"]),
        }
        for numero, (ano_escolar, disciplinas) in base.items():
            ano = AnoCurso(ciclo_id=ciclo.id, numero=numero, ano_escolar=ano_escolar)
            db.session.add(ano)
            db.session.flush()
            for pos, nome_disc in enumerate(disciplinas, start=1):
                tipo = "disciplina"
                if nome_disc.startswith("FCT"):
                    tipo = "fct"
                elif nome_disc.startswith("PAP"):
                    tipo = "pap"
                db.session.add(Disciplina(ano_id=ano.id, nombre=nome_disc, tipo=tipo, orden=pos))
    return ciclo


def ensure_ciclos():
    ciclos = [
        ("CP-AMC", "Curso Profissional - Animação e Mediação Comunitária", "social", "Nível 4", "3 anos", "Curso profissional orientado para intervenção comunitária, animação sociocultural e mediação em contextos sociais."),
        ("CP-CIND", "Curso Profissional - Construção Industrial", "industrial", "Nível 4", "3 anos", "Formação profissional na área da construção industrial, processos técnicos, segurança e execução de projetos."),
        ("CP-DPMM", "Curso Profissional - Desenho de Produto em Madeira e Mobiliário", "madeira", "Nível 4", "3 anos", "Curso focado em desenho de produto, mobiliário, materiais, projeto e soluções ligadas à madeira."),
        ("CP-DIE", "Curso Profissional - Design de Interiores e Exteriores", "design", "Nível 4", "3 anos", "Formação em projeto de espaços interiores e exteriores, representação visual, materiais e comunicação de projeto."),
        ("CP-DEQ", "Curso Profissional - Design de Equipamentos", "design", "Nível 4", "3 anos", "Curso direcionado para design de equipamentos, desenho técnico, ergonomia, materiais e desenvolvimento de produto."),
        ("CP-IE", "Curso Profissional - Instalações Elétricas", "industrial", "Nível 4", "3 anos", "Formação técnica em eletricidade, instalações, manutenção, segurança e sistemas elétricos."),
        ("CP-PMCNC", "Curso Profissional - Programação e Maquinação CNC", "industrial", "Nível 4", "3 anos", "Curso orientado para programação, maquinação CNC, processos industriais, CAD/CAM e controlo de produção."),
        ("CP-SCR", "Curso Profissional - Sistemas de Computação e Redes", "informatica", "Nível 4", "3 anos", "Formação em redes, sistemas, hardware, administração e suporte informático."),
        ("EFA-AG", "Curso EFA - Agente em Geriatria", "efa", "EFA", "Adultos", "Educação e Formação de Adultos na área de geriatria, apoio e cuidados à pessoa idosa."),
        ("EFA-CSD", "Curso EFA - Comunicação e Serviço Digital", "efa", "EFA", "Adultos", "Curso EFA focado em comunicação digital, ferramentas tecnológicas e serviços digitais."),
        ("EFA-IIGR", "Curso EFA - Informática - Instalação e Gestão de Redes", "efa", "EFA", "Adultos", "Formação de adultos na área de informática, instalação, manutenção e gestão de redes."),
        ("EFA-DMCM", "Curso EFA - Desenho de Mobiliário e Construções em Madeira", "efa", "EFA", "Adultos", "Curso EFA ligado ao desenho de mobiliário, construção em madeira e processos técnicos."),
    ]
    for orden, args in enumerate(ciclos, start=1):
        add_or_update_ciclo(*args, orden=orden)
    db.session.commit()
    print("Ciclos formativos e EFA comprobados")


def main():
    app = create_app()
    with app.app_context():
        db.create_all()
        ensure_centro()
        ensure_areas()
        ensure_ciclos()
        print("Seed APPAM completado")


if __name__ == "__main__":
    main()

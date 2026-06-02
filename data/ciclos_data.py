"""Datos fallback de ciclos formativos visibles en la demo APPAM."""

CICLOS_FALLBACK = [
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

DEFAULT_CICLO_ANOS = [
    {
        "numero": 1,
        "ano_escolar": "10º",
        "disciplinas": [
            {"nombre": "Português", "tipo": "disciplina"},
            {"nombre": "Inglês", "tipo": "disciplina"},
            {"nombre": "Área de Integração", "tipo": "disciplina"},
            {"nombre": "Formação Técnica I", "tipo": "disciplina"},
        ],
    },
    {
        "numero": 2,
        "ano_escolar": "11º",
        "disciplinas": [
            {"nombre": "Português", "tipo": "disciplina"},
            {"nombre": "Inglês Técnico", "tipo": "disciplina"},
            {"nombre": "Formação Técnica II", "tipo": "disciplina"},
            {"nombre": "Projeto Técnico", "tipo": "disciplina"},
        ],
    },
    {
        "numero": 3,
        "ano_escolar": "12º",
        "disciplinas": [
            {"nombre": "Formação Técnica III", "tipo": "disciplina"},
            {"nombre": "FCT — Formação em Contexto de Trabalho", "tipo": "fct"},
            {"nombre": "PAP — Prova de Aptidão Profissional", "tipo": "pap"},
        ],
    },
]

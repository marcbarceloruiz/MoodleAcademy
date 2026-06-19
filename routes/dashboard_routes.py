"""
Blueprint: Dashboard / Início do campus.
Rotas:
    /                          → dashboard por role (visitante, aluno, docente, admin)
    /as-minhas-classificacoes  → notas do aluno autenticado
    /as-minhas-tarefas         → tarefas e entregas do aluno
    /calendario                → calendário do campus

Os dados vêm da BD quando as tabelas existem (matriculas, classificacoes,
tarefas, entregas, eventos_campus); caso contrário usa-se o fallback mock
sem rebentar a página.
"""

from flask import Blueprint, render_template, session, url_for

from decorators import login_required
from services.data_service import (
    get_current_user, get_user_courses, get_events,
    get_notices, calculate_course_progress,
    format_date, format_date_short, estado_curso_badge,
)
from services.moodle_service import (
    get_matriculas_usuario,
    get_classificacoes_usuario,
    get_tarefas_usuario,
    get_eventos_campus,
)

dashboard_bp = Blueprint('dashboard', __name__)


# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────

def _eventos_para_dashboard(limit=4):
    """
    Eventos do campus a partir da BD (eventos_campus).
    Fallback: eventos mock de get_events().
    """
    eventos_db = get_eventos_campus(limit=limit, futuros=True)
    if eventos_db:                       # None → tabela em falta; [] → sem futuros
        return eventos_db

    eventos = get_events(limit=limit)
    for ev in eventos:
        ev['_fecha_corta'] = format_date_short(ev['fecha'])
        parts = str(ev.get('fecha', ''))[:10].split('-')
        ev['_dia'] = str(int(parts[2])) if len(parts) == 3 else '--'
        ev['_mes'] = (ev.get('_fecha_corta') or '')[-3:]
    return eventos


def _cursos_do_aluno(usuario_id):
    """
    Cursos do aluno: matrículas reais se existirem; senão mock.
    Normaliza para o formato esperado pelo dashboard
    (titulo, _progreso, _badge, id para o link).
    """
    matriculas = get_matriculas_usuario(usuario_id)

    if matriculas:
        cursos = []
        for m in matriculas:
            cursos.append({
                "id":        m["ciclo_id"],          # liga a /ciclos/<id>
                "titulo":    m["titulo"],
                "tutor":     m.get("area") or m.get("nivel") or "",
                "estado":    m["estado"],
                "_progreso": m.get("progresso") or 0,
                "_badge":    m["_estado_label"],
                "_badge_css": m["_estado_css"],
                "_real":     True,                    # veio de matrículas
            })
        return cursos

    # Fallback mock (compatível com o comportamento anterior)
    cursos = get_user_courses()
    for c in cursos:
        c['_progreso']  = calculate_course_progress(c)
        c['_badge']     = estado_curso_badge(c['estado'])
        c['_badge_css'] = ''
        c['_real']      = False
    return cursos


# ──────────────────────────────────────────────
# DASHBOARD PRINCIPAL
# ──────────────────────────────────────────────

@dashboard_bp.route('/')
def dashboard():
    usuario    = get_current_user()
    usuario_id = session.get("usuario_id")
    roles      = session.get("usuario_roles", [])
    is_aluno   = "aluno" in roles

    eventos       = _eventos_para_dashboard(limit=4)
    todos_eventos = get_eventos_campus(futuros=True) or get_events()
    avisos        = get_notices()

    # Dados específicos do aluno (matrículas, notas, tarefas)
    mis_cursos        = []
    classificacoes    = []
    tarefas_pendentes = []
    if is_aluno and usuario_id:
        mis_cursos        = _cursos_do_aluno(usuario_id)
        classificacoes    = get_classificacoes_usuario(usuario_id, limit=3)
        tarefas_pendentes = get_tarefas_usuario(usuario_id, so_pendentes=True)[:3]
    elif is_aluno:
        mis_cursos = _cursos_do_aluno(None)

    return render_template(
        'dashboard.html',
        usuario=usuario,
        mis_cursos=mis_cursos,
        eventos=eventos,
        todos_eventos=todos_eventos,
        avisos=avisos,
        total_proximos=len(todos_eventos),
        classificacoes=classificacoes,
        tarefas_pendentes=tarefas_pendentes,
        format_date=format_date,
        format_date_short=format_date_short,
    )


# ──────────────────────────────────────────────
# AS MINHAS CLASSIFICAÇÕES
# ──────────────────────────────────────────────

@dashboard_bp.route('/as-minhas-classificacoes')
@login_required
def classificacoes():
    usuario    = get_current_user()
    usuario_id = session.get("usuario_id")

    notas = get_classificacoes_usuario(usuario_id)

    return render_template(
        'classificacoes.html',
        usuario=usuario,
        notas=notas,
    )


# ──────────────────────────────────────────────
# AS MINHAS TAREFAS
# ──────────────────────────────────────────────

@dashboard_bp.route('/as-minhas-tarefas')
@login_required
def tarefas():
    usuario    = get_current_user()
    usuario_id = session.get("usuario_id")

    lista = get_tarefas_usuario(usuario_id)
    pendentes = [t for t in lista if t["estado"] == "pendente"]
    feitas    = [t for t in lista if t["estado"] != "pendente"]

    return render_template(
        'tarefas.html',
        usuario=usuario,
        tarefas_pendentes=pendentes,
        tarefas_feitas=feitas,
        total=len(lista),
    )




def _date_iso(value):
    """Converte date/datetime/string em YYYY-MM-DD para o calendário visual."""
    if not value:
        return ""
    return str(value)[:10]


_CAL_TIPO_LABELS = {
    "avaliacao": ("📝", "Avaliação"),
    "entrega": ("📤", "Entrega"),
    "fct": ("🏢", "FCT"),
    "pap": ("🎓", "PAP"),
    "evento": ("📅", "Evento da escola"),
    "tarefa": ("📌", "Tarefa"),
}


def _build_calendar_events(eventos, tarefas_cal):
    """
    Normaliza eventos e tarefas para JSON consumido pelo calendário visual.
    Não altera a lógica existente; só prepara dados para o frontend.
    """
    calendar_events = []

    for ev in eventos or []:
        tipo = (ev.get("tipo") or "evento").lower()
        icon, label = _CAL_TIPO_LABELS.get(tipo, _CAL_TIPO_LABELS["evento"])
        date = _date_iso(ev.get("data_evento") or ev.get("fecha"))
        if not date:
            continue
        calendar_events.append({
            "title": ev.get("titulo") or "Evento",
            "date": date,
            "time": ev.get("hora") or "",
            "type": tipo if tipo in _CAL_TIPO_LABELS else "evento",
            "typeLabel": ev.get("_tipo_label") or label,
            "icon": ev.get("_icone") or icon,
            "description": ev.get("descricao") or ev.get("descripcion") or "",
            "disciplina": ev.get("disciplina") or "",
            "estado": ev.get("estado") or "",
            "url": "",
        })

    for t in tarefas_cal or []:
        date = _date_iso(t.get("data_limite") or t.get("fecha"))
        if not date:
            continue
        icon, label = _CAL_TIPO_LABELS["tarefa"]
        calendar_events.append({
            "title": t.get("titulo") or "Tarefa",
            "date": date,
            "time": "23:59",
            "type": "tarefa",
            "typeLabel": label,
            "icon": icon,
            "description": t.get("descricao") or "",
            "disciplina": t.get("disciplina") or "",
            "estado": t.get("_estado_label") or t.get("estado") or "",
            "url": url_for("dashboard.tarefas"),
        })

    return calendar_events


# ──────────────────────────────────────────────
# CALENDÁRIO DO CAMPUS
# ──────────────────────────────────────────────

@dashboard_bp.route('/calendario')
@login_required
def calendario():
    usuario    = get_current_user()
    usuario_id = session.get("usuario_id")

    eventos = get_eventos_campus(futuros=True)
    if eventos is None:
        # Tabela em falta → usa mock
        eventos = []
        for ev in get_events():
            parts = str(ev.get('fecha', ''))[:10].split('-')
            ev['_dia'] = str(int(parts[2])) if len(parts) == 3 else '--'
            ev['_mes'] = format_date_short(ev['fecha'])[-3:]
            ev['_data_fmt']   = format_date(ev['fecha'])
            ev['_icone']      = '📅'
            ev['_tipo_label'] = 'Evento'
            eventos.append(ev)

    # Tarefas com prazo também entram no calendário do aluno
    tarefas_cal = []
    if usuario_id and "aluno" in session.get("usuario_roles", []):
        tarefas_cal = get_tarefas_usuario(usuario_id, so_pendentes=True)

    calendar_events = _build_calendar_events(eventos, tarefas_cal)

    return render_template(
        'calendario.html',
        usuario=usuario,
        eventos=eventos,
        tarefas_cal=tarefas_cal,
        calendar_events=calendar_events,
    )

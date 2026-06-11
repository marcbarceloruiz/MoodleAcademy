"""
moodle_service.py
=================
Academia Profissional Prof. Albino de Matos — Escola Profissional Vértice

Serviço para as funcionalidades tipo Moodle:
  • Matrículas (aluno ↔ ciclo)
  • Classificações
  • Tarefas e entregas
  • Eventos do campus (calendário)
  • Notificações

REGRA DE OURO: nenhuma função deste módulo pode rebentar a página.
Se a tabela não existir ou a query falhar → devolve fallback demo
e regista um aviso na consola.
"""

from sqlalchemy import text
from extensions import db


# ──────────────────────────────────────────────
# HELPERS INTERNOS
# ──────────────────────────────────────────────

def _safe_fetch_all(sql, params=None, context=""):
    """
    Executa SELECT e devolve lista de dicts.
    Em caso de erro (tabela em falta, etc.) devolve None e avisa na consola.
    """
    try:
        rows = db.session.execute(text(sql), params or {}).mappings().all()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"[moodle_service] Aviso ({context}): {e}")
        return None


def _fmt_date_pt(value):
    """2026-06-18 → '18 jun 2026' (sem depender de locale)."""
    meses = ["jan", "fev", "mar", "abr", "mai", "jun",
             "jul", "ago", "set", "out", "nov", "dez"]
    try:
        s = str(value)[:10]
        y, m, d = s.split("-")
        return f"{int(d)} {meses[int(m) - 1]} {y}"
    except Exception:
        return str(value) if value else ""


def _dia_mes(value):
    """2026-06-18 → ('18', 'jun') para os blocos de data do dashboard."""
    meses = ["jan", "fev", "mar", "abr", "mai", "jun",
             "jul", "ago", "set", "out", "nov", "dez"]
    try:
        s = str(value)[:10]
        _, m, d = s.split("-")
        return str(int(d)), meses[int(m) - 1]
    except Exception:
        return "--", "---"


# ──────────────────────────────────────────────
# MATRÍCULAS
# ──────────────────────────────────────────────

def get_matriculas_usuario(usuario_id):
    """
    Cursos em que o utilizador está matriculado, com progresso e estado.
    Devolve [] se não houver dados; fallback None nunca chega ao template.
    """
    if not usuario_id:
        return []

    rows = _safe_fetch_all("""
        SELECT
            m.id            AS matricula_id,
            m.estado,
            m.progresso,
            m.data_matricula,
            c.id            AS ciclo_id,
            c.codigo,
            c.nombre        AS titulo,
            c.area,
            c.nivel
        FROM matriculas m
        JOIN ciclos_formativos c ON c.id = m.ciclo_id
        WHERE m.usuario_id = :uid
        ORDER BY m.estado = 'em_curso' DESC, m.progresso DESC
    """, {"uid": usuario_id}, context="get_matriculas_usuario")

    if rows is None:
        return []

    badges = {
        "em_curso":  ("Em curso",  "status-en-progreso"),
        "concluido": ("Concluído", "status-completado"),
        "pendente":  ("Pendente",  "status-no-comenzado"),
    }
    for r in rows:
        label, css = badges.get(r["estado"], ("Em curso", "status-en-progreso"))
        r["_estado_label"] = label
        r["_estado_css"]   = css
        r["_data_fmt"]     = _fmt_date_pt(r.get("data_matricula"))
    return rows


# ──────────────────────────────────────────────
# CLASSIFICAÇÕES
# ──────────────────────────────────────────────

def get_classificacoes_usuario(usuario_id, limit=None):
    """
    Notas do utilizador, mais recentes primeiro.
    """
    if not usuario_id:
        return []

    sql = """
        SELECT id, disciplina, tipo_avaliacao, nota, observacao, data_avaliacao
        FROM classificacoes
        WHERE usuario_id = :uid
        ORDER BY data_avaliacao DESC, id DESC
    """
    if limit:
        sql += " LIMIT :lim"

    rows = _safe_fetch_all(
        sql,
        {"uid": usuario_id, "lim": limit} if limit else {"uid": usuario_id},
        context="get_classificacoes_usuario",
    )
    if rows is None:
        return []

    for r in rows:
        r["_data_fmt"] = _fmt_date_pt(r.get("data_avaliacao"))
        nota = r.get("nota")
        r["_nota_fmt"] = (f"{float(nota):.1f}".rstrip("0").rstrip(".")
                          if nota is not None else "—")
        try:
            n = float(nota) if nota is not None else None
        except Exception:
            n = None
        r["_nota_css"] = ("nota-alta" if n is not None and n >= 14
                          else "nota-media" if n is not None and n >= 10
                          else "nota-baixa" if n is not None
                          else "nota-na")
    return rows


# ──────────────────────────────────────────────
# TAREFAS E ENTREGAS
# ──────────────────────────────────────────────

def get_tarefas_usuario(usuario_id, so_pendentes=False):
    """
    Tarefas com o estado de entrega do utilizador.
    Tarefas sem registo em `entregas` aparecem como 'pendente'.
    """
    if not usuario_id:
        return []

    rows = _safe_fetch_all("""
        SELECT
            t.id,
            t.titulo,
            t.descricao,
            t.disciplina,
            t.data_limite,
            COALESCE(e.estado, 'pendente') AS estado,
            e.ficheiro_url,
            e.nota,
            e.data_entrega
        FROM tarefas t
        LEFT JOIN entregas e
               ON e.tarefa_id = t.id AND e.usuario_id = :uid
        ORDER BY t.data_limite ASC, t.id ASC
    """, {"uid": usuario_id}, context="get_tarefas_usuario")

    if rows is None:
        return []

    badges = {
        "pendente": ("Pendente",  "ab-pendiente"),
        "entregue": ("Entregue",  "ab-abierto"),
        "avaliado": ("Avaliado",  "ab-completado"),
    }
    out = []
    for r in rows:
        if so_pendentes and r["estado"] != "pendente":
            continue
        label, css = badges.get(r["estado"], ("Pendente", "ab-pendiente"))
        r["_estado_label"] = label
        r["_estado_css"]   = css
        r["_limite_fmt"]   = _fmt_date_pt(r.get("data_limite"))
        d, m = _dia_mes(r.get("data_limite"))
        r["_dia"], r["_mes"] = d, m
        nota = r.get("nota")
        r["_nota_fmt"] = (f"{float(nota):.1f}".rstrip("0").rstrip(".")
                          if nota is not None else None)
        out.append(r)
    return out


# ──────────────────────────────────────────────
# EVENTOS DO CAMPUS (CALENDÁRIO)
# ──────────────────────────────────────────────

_TIPO_EVENTO = {
    "avaliacao": ("📝", "Avaliação"),
    "entrega":   ("📤", "Entrega"),
    "fct":       ("🏢", "FCT"),
    "pap":       ("🎓", "PAP"),
    "evento":    ("📅", "Evento"),
}


def get_eventos_campus(limit=None, futuros=True):
    """
    Eventos do calendário do campus (tabela eventos_campus).
    Devolve None se a tabela não existir → o caller usa o fallback mock.
    """
    sql = """
        SELECT id, titulo, tipo, data_evento, hora, descricao
        FROM eventos_campus
    """
    if futuros:
        sql += " WHERE data_evento >= CURDATE() "
    sql += " ORDER BY data_evento ASC, hora ASC "
    if limit:
        sql += " LIMIT :lim"

    rows = _safe_fetch_all(
        sql, {"lim": limit} if limit else {}, context="get_eventos_campus"
    )
    if rows is None:
        return None     # caller decide o fallback

    for r in rows:
        icon, label = _TIPO_EVENTO.get(r.get("tipo"), ("📅", "Evento"))
        r["_icone"]      = icon
        r["_tipo_label"] = label
        r["_data_fmt"]   = _fmt_date_pt(r.get("data_evento"))
        d, m = _dia_mes(r.get("data_evento"))
        r["_dia"], r["_mes"] = d, m
        # Compatibilidade com os templates antigos (ev.fecha / ev.hora)
        r["fecha"]  = str(r.get("data_evento"))[:10]
        r["titulo"] = r.get("titulo")
        r["hora"]   = r.get("hora") or ""
    return rows


# ──────────────────────────────────────────────
# NOTIFICAÇÕES
# ──────────────────────────────────────────────

_NOTIF_FALLBACK = [
    {"titulo": "Bem-vindo ao Campus Virtual",
     "mensagem": "Explora os ciclos formativos e o portal institucional.",
     "tipo": "info", "_data_fmt": ""},
]

_TIPO_NOTIF = {
    "info":      "🔵",
    "aviso":     "🟠",
    "avaliacao": "🟢",
    "sistema":   "⚙️",
}


def get_notificacoes_usuario(usuario_id=None, limit=6):
    """
    Notificações do utilizador + globais (usuario_id IS NULL).
    Sempre devolve lista (fallback demo se a tabela não existir).
    """
    rows = _safe_fetch_all("""
        SELECT id, titulo, mensagem, tipo, lida, criado_em
        FROM notificacoes
        WHERE usuario_id IS NULL
           OR usuario_id = :uid
        ORDER BY criado_em DESC, id DESC
        LIMIT :lim
    """, {"uid": usuario_id or 0, "lim": limit},
        context="get_notificacoes_usuario")

    if rows is None:
        return list(_NOTIF_FALLBACK)

    for r in rows:
        r["_icone"]    = _TIPO_NOTIF.get(r.get("tipo"), "🔵")
        r["_data_fmt"] = _fmt_date_pt(str(r.get("criado_em"))[:10])
    return rows

"""
Blueprint: Administración.
Ruta: /admin

Panel provisional de administración del campus.
De momento no hay login real, así que esta zona es solo para desarrollo.
"""

import os
import uuid

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    current_app,
    flash,              # ← AÑADIDO para mensajes de feedback
    abort,
)
from sqlalchemy import text
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash

from extensions import db, mail
from flask_mail import Message
from services.data_service import get_current_user, get_centro

admin_bp = Blueprint("admin", __name__)


# ──────────────────────────────────────────────
# AUTENTICACIÓN SIMPLE DEL ADMIN
# ──────────────────────────────────────────────

def _admin_autenticado():
    """
    Comprueba si la sesión actual tiene acceso al panel admin.
    """
    return session.get("admin_ok") is True


@admin_bp.before_request
def proteger_admin():
    """
    Protege todas las rutas del blueprint admin.
    """
    rutas_libres = {
        "admin.admin_login",
        "admin.admin_logout",
    }

    if request.endpoint in rutas_libres:
        return None

    if not _admin_autenticado():
        return redirect(url_for("admin.admin_login"))

    return None


@admin_bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """
    Login básico del panel de administración.
    """
    if _admin_autenticado():
        return redirect(url_for("admin.admin"))

    error = None
    usuario = get_current_user()
    centro = get_centro()

    if request.method == "POST":
        password = request.form.get("password", "")
        admin_password = current_app.config.get("ADMIN_PASSWORD", "")

        if not admin_password:
            error = "Painel não configurado. Defina ADMIN_PASSWORD em .env."
        elif admin_password.startswith(("scrypt:", "pbkdf2:")):
            # Palavra-passe armazenada como hash werkzeug (modo seguro)
            if check_password_hash(admin_password, password):
                session["admin_ok"] = True
                session.permanent = False
                return redirect(url_for("admin.admin"))
            error = "Palavra-passe incorreta."
        else:
            # Compatibilidade: texto simples em desenvolvimento
            # Para produção, substituir ADMIN_PASSWORD por um hash gerado com:
            # python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('a_tua_password'))"
            if password == admin_password:
                session["admin_ok"] = True
                session.permanent = False
                return redirect(url_for("admin.admin"))
            error = "Palavra-passe incorreta."

    return render_template(
        "admin_login.html",
        error=error,
        usuario=usuario,
        centro=centro,
    )


@admin_bp.route("/admin/logout", methods=["POST"])
def admin_logout():
    """
    Cierra la sesión del panel admin (legacy y nuevo sistema).
    """
    for key in ("admin_ok", "usuario_id", "usuario_username",
                "usuario_nome", "usuario_roles"):
        session.pop(key, None)
    return redirect(url_for("admin.admin_login"))


def _as_bool(value):
    return 1 if str(value) == "1" else 0


def _checkbox_value(field_name):
    """
    Lee correctamente checkboxes que tienen hidden value=0 + checkbox value=1.
    Si llega algún '1', significa marcado.
    """
    values = request.form.getlist(field_name)
    return 1 if "1" in values else 0


def _to_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default


def _fetch_all(sql, params=None):
    try:
        return db.session.execute(text(sql), params or {}).mappings().all()
    except Exception as e:
        current_app.logger.error("[admin] _fetch_all: %s", e, exc_info=True)
        return []


def _fetch_one(sql, params=None):
    try:
        return db.session.execute(text(sql), params or {}).mappings().first()
    except Exception as e:
        current_app.logger.error("[admin] _fetch_one: %s", e, exc_info=True)
        return None


def _allowed_upload(filename):
    """
    Comprueba si el archivo tiene una extensión permitida.
    """
    if not filename or "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()
    allowed = current_app.config.get(
        "ALLOWED_UPLOAD_EXTENSIONS",
        {
            "pdf",
            "doc",
            "docx",
            "xls",
            "xlsx",
            "ppt",
            "pptx",
            "txt",
            "png",
            "jpg",
            "jpeg",
            "webp",
        },
    )

    return extension in allowed


def _save_uploaded_file(field_name, subfolder):
    """
    Guarda un archivo subido desde un formulario del admin.

    Devuelve una URL pública tipo:
    /static/uploads/documentos/archivo.pdf

    Si no se sube ningún archivo, devuelve None.
    """
    uploaded_file = request.files.get(field_name)

    if not uploaded_file or not uploaded_file.filename:
        return None

    if not _allowed_upload(uploaded_file.filename):
        raise ValueError("Tipo de archivo no permitido.")

    original_name = secure_filename(uploaded_file.filename)
    extension = original_name.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{extension}"

    upload_root = current_app.config.get("UPLOAD_FOLDER")
    if not upload_root:
        upload_root = os.path.join(current_app.root_path, "static", "uploads")

    destination_folder = os.path.join(upload_root, subfolder)
    os.makedirs(destination_folder, exist_ok=True)

    destination_path = os.path.join(destination_folder, unique_name)
    uploaded_file.save(destination_path)

    return f"/static/uploads/{subfolder}/{unique_name}"


def _delete_uploaded_file(url):
    """
    Borra un archivo local de /static/uploads si existe.

    Solo elimina rutas internas que empiecen por /static/uploads/.
    No toca URLs externas tipo https://...
    """
    if not url:
        return

    if not str(url).startswith("/static/uploads/"):
        return

    try:
        relative_path = str(url).lstrip("/").replace("/", os.sep)
        file_path = os.path.abspath(
            os.path.join(current_app.root_path, relative_path)
        )

        uploads_root = os.path.abspath(
            os.path.join(current_app.root_path, "static", "uploads")
        )

        # Seguridad: evita borrar fuera de static/uploads
        if not file_path.startswith(uploads_root):
            return

        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as e:
        current_app.logger.error("Error eliminando archivo subido: %s", e, exc_info=True)


def _delete_uploaded_files(urls):
    """
    Borra una lista de archivos locales subidos.
    """
    for url in urls or []:
        _delete_uploaded_file(url)


def _admin_stats():
    stats = {}

    queries = {
        "total_areas": "SELECT COUNT(*) AS total FROM areas_institucionais",
        "total_documentos": "SELECT COUNT(*) AS total FROM documentos_institucionais",
        "total_ciclos": "SELECT COUNT(*) AS total FROM ciclos_formativos",
        "total_disciplinas": "SELECT COUNT(*) AS total FROM disciplinas_ciclo",
        "total_secciones": "SELECT COUNT(*) AS total FROM secciones_disciplina",
        "total_recursos": "SELECT COUNT(*) AS total FROM recursos_disciplina",
    }

    for key, sql in queries.items():
        try:
            row = _fetch_one(sql)
            stats[key] = row["total"] if row else 0
        except Exception as e:
            current_app.logger.error("Error calculando estadística %s: %s", key, e, exc_info=True)
            stats[key] = 0

    return stats


def _load_areas():
    return _fetch_all("""
        SELECT
            id,
            slug,
            titulo,
            descricao,
            conteudo,
            ativo
        FROM areas_institucionais
        ORDER BY id ASC
    """)


def _load_documentos():
    return _fetch_all("""
        SELECT
            d.id,
            d.area_id,
            d.titulo,
            d.tipo,
            d.descricao,
            d.url,
            d.orden,
            d.visible,
            a.slug AS area_slug,
            a.titulo AS area_titulo
        FROM documentos_institucionais d
        JOIN areas_institucionais a ON a.id = d.area_id
        ORDER BY a.id ASC, d.orden ASC, d.id ASC
    """)


def _load_ciclos():
    return _fetch_all("""
        SELECT
            id,
            codigo,
            nombre,
            area,
            nivel,
            duracion,
            descripcion,
            activo,
            orden
        FROM ciclos_formativos
        ORDER BY orden ASC, id ASC
    """)


def _load_anos_for_select():
    """
    Carga los años de cada ciclo para poder crear disciplinas desde el admin.
    """
    return _fetch_all("""
        SELECT
            a.id,
            a.numero,
            a.ano_escolar,
            c.codigo AS ciclo_codigo,
            c.nombre AS ciclo_nombre
        FROM anos_ciclo a
        JOIN ciclos_formativos c ON c.id = a.ciclo_id
        ORDER BY c.orden ASC, c.id ASC, a.numero ASC
    """)


def _load_disciplinas(limit=300):
    return _fetch_all("""
        SELECT
            d.id,
            d.codigo,
            d.nombre,
            d.tipo,
            d.horas,
            d.descripcion,
            a.ano_escolar,
            c.nombre AS ciclo_nombre,
            c.codigo AS ciclo_codigo
        FROM disciplinas_ciclo d
        JOIN anos_ciclo a ON a.id = d.ano_id
        JOIN ciclos_formativos c ON c.id = a.ciclo_id
        ORDER BY c.orden ASC, a.numero ASC, d.orden ASC, d.id ASC
        LIMIT :limit
    """, {"limit": limit})


def _load_secciones(limit=1000):
    """
    Carga secciones para la pestaña Admin > Secciones.
    Usa LEFT JOIN para que no falle si alguna relación está incompleta.
    """
    try:
        return _fetch_all("""
            SELECT
                s.id,
                s.titulo,
                s.slug,
                s.descripcion,
                s.orden,
                s.visible,
                d.nombre AS disciplina_nombre,
                a.ano_escolar,
                c.codigo AS ciclo_codigo,
                c.nombre AS ciclo_nombre
            FROM secciones_disciplina s
            LEFT JOIN disciplinas_ciclo d ON d.id = s.disciplina_id
            LEFT JOIN anos_ciclo a ON a.id = d.ano_id
            LEFT JOIN ciclos_formativos c ON c.id = a.ciclo_id
            ORDER BY c.orden ASC, d.id ASC, s.orden ASC, s.id ASC
            LIMIT :limit
        """, {"limit": limit})

    except Exception as e:
        current_app.logger.error("Error cargando secciones de disciplinas: %s", e, exc_info=True)
        return []


def _load_secciones_for_select():
    """
    Carga secciones para el selector de creación de recursos.
    """
    return _fetch_all("""
        SELECT
            s.id,
            s.titulo,
            s.slug,
            d.nombre AS disciplina_nombre,
            a.ano_escolar,
            c.codigo AS ciclo_codigo,
            c.nombre AS ciclo_nombre
        FROM secciones_disciplina s
        JOIN disciplinas_ciclo d ON d.id = s.disciplina_id
        JOIN anos_ciclo a ON a.id = d.ano_id
        JOIN ciclos_formativos c ON c.id = a.ciclo_id
        ORDER BY c.orden ASC, d.id ASC, s.orden ASC, s.id ASC
    """)


def _load_recursos(limit=120):
    return _fetch_all("""
        SELECT
            r.id,
            r.titulo,
            r.tipo,
            r.descripcion,
            r.url,
            r.orden,
            r.visible,
            r.data_limite,
            s.titulo AS seccion_titulo,
            s.slug AS seccion_slug,
            d.nombre AS disciplina_nombre,
            c.nombre AS ciclo_nombre
        FROM recursos_disciplina r
        JOIN secciones_disciplina s ON s.id = r.seccion_id
        JOIN disciplinas_ciclo d ON d.id = s.disciplina_id
        JOIN anos_ciclo a ON a.id = d.ano_id
        JOIN ciclos_formativos c ON c.id = a.ciclo_id
        ORDER BY c.orden ASC, d.id ASC, s.orden ASC, r.orden ASC
        LIMIT :limit
    """, {"limit": limit})


@admin_bp.route("/admin")
def admin():
    usuario = get_current_user()
    centro = get_centro()
    tab = request.args.get("tab", "portal")

    stats = _admin_stats()
    areas = _load_areas()
    documentos = _load_documentos()
    ciclos = _load_ciclos()
    anos = _load_anos_for_select()
    disciplinas = _load_disciplinas()
    secciones_admin = _load_secciones()
    secciones = _load_secciones_for_select()
    recursos = _load_recursos()

    alunos = []
    classificacoes_admin = []
    if tab == "avaliacoes":
        alunos = _fetch_all("""
            SELECT u.id, u.nome, u.username
            FROM usuarios u
            JOIN usuario_roles ur ON ur.usuario_id = u.id
            JOIN roles r ON r.id = ur.role_id
            WHERE r.nome = 'aluno'
            ORDER BY u.nome ASC
        """)
        classificacoes_admin = _fetch_all("""
            SELECT
                c.id,
                c.usuario_id,
                c.disciplina,
                c.tipo_avaliacao,
                c.nota,
                c.observacao,
                c.data_avaliacao,
                u.nome AS aluno_nome,
                u.username AS aluno_username
            FROM classificacoes c
            LEFT JOIN usuarios u ON u.id = c.usuario_id
            ORDER BY c.criado_em DESC
            LIMIT 200
        """)

    return render_template(
        "admin.html",
        usuario=usuario,
        centro=centro,
        tab=tab,
        stats=stats,
        areas=areas,
        documentos=documentos,
        ciclos=ciclos,
        anos=anos,
        disciplinas=disciplinas,
        secciones_admin=secciones_admin,
        secciones=secciones,
        recursos=recursos,
        alunos=alunos,
        classificacoes_admin=classificacoes_admin,
    )


# ──────────────────────────────────────────────
# PORTAL — Áreas institucionales
# ──────────────────────────────────────────────

@admin_bp.route("/admin/areas/<int:area_id>/update", methods=["POST"])
def update_area(area_id):
    try:
        db.session.execute(
            text("""
                UPDATE areas_institucionais
                SET
                    titulo = :titulo,
                    descricao = :descricao,
                    conteudo = :conteudo,
                    ativo = :ativo
                WHERE id = :area_id
            """),
            {
                "area_id": area_id,
                "titulo": request.form.get("titulo", "").strip(),
                "descricao": request.form.get("descricao", "").strip(),
                "conteudo": request.form.get("conteudo", "").strip(),
                "ativo": _checkbox_value("ativo"),
            },
        )
        db.session.commit()
        flash("Secção do portal atualizada.", "success")

    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Error actualizando área institucional: %s", e, exc_info=True)
        flash("Erro ao atualizar a secção do portal.", "danger")

    return redirect(url_for("admin.admin", tab="portal"))


# ──────────────────────────────────────────────
# DOCUMENTOS
# ──────────────────────────────────────────────

@admin_bp.route("/admin/documentos/create", methods=["POST"])
def create_documento():
    try:
        area_id = _to_int(request.form.get("area_id"))
        titulo = request.form.get("titulo", "").strip()

        if titulo and area_id:
            uploaded_url = _save_uploaded_file("archivo", "documentos")
            url = uploaded_url or request.form.get("url", "").strip() or None

            db.session.execute(
                text("""
                    INSERT IGNORE INTO documentos_institucionais
                    (area_id, titulo, tipo, descricao, url, orden, visible)
                    SELECT
                        :area_id,
                        :titulo,
                        :tipo,
                        :descricao,
                        :url,
                        COALESCE(MAX(orden), 0) + 1,
                        1
                    FROM documentos_institucionais
                    WHERE area_id = :area_id
                """),
                {
                    "area_id": area_id,
                    "titulo": titulo,
                    "tipo": request.form.get("tipo", "Documento").strip(),
                    "descricao": request.form.get("descricao", "").strip(),
                    "url": url,
                },
            )
            db.session.commit()
            flash("Documento criado com sucesso.", "success")
        else:
            flash("Faltam dados obrigatórios (título e área).", "warning")

    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Error creando documento institucional: %s", e, exc_info=True)
        flash("Erro ao criar o documento.", "danger")

    return redirect(url_for("admin.admin", tab="documentos"))


@admin_bp.route("/admin/documentos/<int:documento_id>/update", methods=["POST"])
def update_documento(documento_id):
    try:
        documento = _fetch_one("""
            SELECT url
            FROM documentos_institucionais
            WHERE id = :documento_id
            LIMIT 1
        """, {"documento_id": documento_id})

        old_url = documento["url"] if documento else None

        uploaded_url = _save_uploaded_file("archivo", "documentos")
        url = uploaded_url or request.form.get("url", "").strip() or None

        db.session.execute(
            text("""
                UPDATE documentos_institucionais
                SET
                    titulo = :titulo,
                    tipo = :tipo,
                    descricao = :descricao,
                    url = :url,
                    orden = :orden,
                    visible = :visible
                WHERE id = :documento_id
            """),
            {
                "documento_id": documento_id,
                "titulo": request.form.get("titulo", "").strip(),
                "tipo": request.form.get("tipo", "Documento").strip(),
                "descricao": request.form.get("descricao", "").strip(),
                "url": url,
                "orden": _to_int(request.form.get("orden"), 0),
                "visible": _checkbox_value("visible"),
            },
        )
        db.session.commit()

        if uploaded_url and old_url:
            _delete_uploaded_file(old_url)

        flash("Documento atualizado com sucesso.", "success")

    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Error actualizando documento institucional: %s", e, exc_info=True)
        flash("Erro ao atualizar o documento.", "danger")

    return redirect(url_for("admin.admin", tab="documentos"))


@admin_bp.route("/admin/documentos/<int:documento_id>/toggle", methods=["POST"])
def toggle_documento(documento_id):
    try:
        db.session.execute(
            text("""
                UPDATE documentos_institucionais
                SET visible = CASE WHEN visible = 1 THEN 0 ELSE 1 END
                WHERE id = :documento_id
            """),
            {"documento_id": documento_id},
        )
        db.session.commit()
        flash("Visibilidade do documento atualizada.", "info")

    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Error cambiando visibilidad del documento institucional: %s", e, exc_info=True)
        flash("Erro ao alterar a visibilidade do documento.", "danger")

    return redirect(url_for("admin.admin", tab="documentos"))


@admin_bp.route("/admin/documentos/<int:documento_id>/delete", methods=["POST"])
def delete_documento(documento_id):
    try:
        documento = _fetch_one("""
            SELECT url
            FROM documentos_institucionais
            WHERE id = :documento_id
            LIMIT 1
        """, {"documento_id": documento_id})

        old_url = documento["url"] if documento else None

        db.session.execute(
            text("""
                DELETE FROM documentos_institucionais
                WHERE id = :documento_id
            """),
            {"documento_id": documento_id},
        )
        db.session.commit()

        _delete_uploaded_file(old_url)
        flash("Documento eliminado com sucesso.", "success")

    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Error eliminando documento institucional: %s", e, exc_info=True)
        flash("Erro ao eliminar o documento.", "danger")

    return redirect(url_for("admin.admin", tab="documentos"))


# ──────────────────────────────────────────────
# CICLOS FORMATIVOS
# ──────────────────────────────────────────────

@admin_bp.route("/admin/ciclos/create", methods=["POST"])
def create_ciclo():
    """
    Crea un ciclo formativo y genera automáticamente sus 3 años:
    10º ano, 11º ano y 12º ano.
    """
    try:
        codigo = request.form.get("codigo", "").strip()
        nombre = request.form.get("nombre", "").strip()

        if codigo and nombre:
            result = db.session.execute(
                text("""
                    INSERT INTO ciclos_formativos
                    (codigo, nombre, area, nivel, duracion, descripcion, activo, orden)
                    VALUES
                    (:codigo, :nombre, :area, :nivel, :duracion, :descripcion, 1, :orden)
                """),
                {
                    "codigo": codigo,
                    "nombre": nombre,
                    "area": request.form.get("area", "").strip(),
                    "nivel": request.form.get("nivel", "Nível 4").strip(),
                    "duracion": request.form.get("duracion", "3 anos").strip(),
                    "descripcion": request.form.get("descripcion", "").strip(),
                    "orden": _to_int(request.form.get("orden"), 999),
                },
            )

            ciclo_id = result.lastrowid

            if ciclo_id:
                anos_base = [
                    (1, "10º ano"),
                    (2, "11º ano"),
                    (3, "12º ano"),
                ]

                for numero, ano_escolar in anos_base:
                    db.session.execute(
                        text("""
                            INSERT INTO anos_ciclo
                            (ciclo_id, numero, ano_escolar)
                            VALUES
                            (:ciclo_id, :numero, :ano_escolar)
                        """),
                        {
                            "ciclo_id": ciclo_id,
                            "numero": numero,
                            "ano_escolar": ano_escolar,
                        },
                    )

            db.session.commit()
            flash("Ciclo formativo criado com os 3 anos (10.º, 11.º e 12.º).", "success")
        else:
            flash("Faltam dados obrigatórios (código e nome).", "warning")

    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Error creando ciclo formativo: %s", e, exc_info=True)
        flash("Erro ao criar o ciclo formativo.", "danger")

    return redirect(url_for("admin.admin", tab="ciclos"))


@admin_bp.route("/admin/ciclos/<int:ciclo_id>/update", methods=["POST"])
def update_ciclo(ciclo_id):
    try:
        db.session.execute(
            text("""
                UPDATE ciclos_formativos
                SET
                    codigo = :codigo,
                    nombre = :nombre,
                    area = :area,
                    nivel = :nivel,
                    duracion = :duracion,
                    descripcion = :descripcion,
                    activo = :activo,
                    orden = :orden
                WHERE id = :ciclo_id
            """),
            {
                "ciclo_id": ciclo_id,
                "codigo": request.form.get("codigo", "").strip(),
                "nombre": request.form.get("nombre", "").strip(),
                "area": request.form.get("area", "").strip(),
                "nivel": request.form.get("nivel", "").strip(),
                "duracion": request.form.get("duracion", "").strip(),
                "descripcion": request.form.get("descripcion", "").strip(),
                "activo": _checkbox_value("activo"),
                "orden": _to_int(request.form.get("orden"), 0),
            },
        )
        db.session.commit()
        flash("Ciclo formativo atualizado.", "success")

    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Error actualizando ciclo formativo: %s", e, exc_info=True)
        flash("Erro ao atualizar o ciclo formativo.", "danger")

    return redirect(url_for("admin.admin", tab="ciclos"))


@admin_bp.route("/admin/ciclos/<int:ciclo_id>/delete", methods=["POST"])
def delete_ciclo(ciclo_id):
    """
    Elimina un ciclo completo:
    recursos -> secciones -> disciplinas -> años -> ciclo.
    También borra los archivos físicos de los recursos asociados.
    """
    try:
        recursos = _fetch_all("""
            SELECT r.url
            FROM recursos_disciplina r
            JOIN secciones_disciplina s ON s.id = r.seccion_id
            JOIN disciplinas_ciclo d ON d.id = s.disciplina_id
            JOIN anos_ciclo a ON a.id = d.ano_id
            WHERE a.ciclo_id = :ciclo_id
        """, {"ciclo_id": ciclo_id})

        urls_to_delete = [r["url"] for r in recursos if r.get("url")]

        db.session.execute(
            text("""
                DELETE r
                FROM recursos_disciplina r
                JOIN secciones_disciplina s ON s.id = r.seccion_id
                JOIN disciplinas_ciclo d ON d.id = s.disciplina_id
                JOIN anos_ciclo a ON a.id = d.ano_id
                WHERE a.ciclo_id = :ciclo_id
            """),
            {"ciclo_id": ciclo_id},
        )

        db.session.execute(
            text("""
                DELETE s
                FROM secciones_disciplina s
                JOIN disciplinas_ciclo d ON d.id = s.disciplina_id
                JOIN anos_ciclo a ON a.id = d.ano_id
                WHERE a.ciclo_id = :ciclo_id
            """),
            {"ciclo_id": ciclo_id},
        )

        db.session.execute(
            text("""
                DELETE d
                FROM disciplinas_ciclo d
                JOIN anos_ciclo a ON a.id = d.ano_id
                WHERE a.ciclo_id = :ciclo_id
            """),
            {"ciclo_id": ciclo_id},
        )

        db.session.execute(
            text("""
                DELETE FROM anos_ciclo
                WHERE ciclo_id = :ciclo_id
            """),
            {"ciclo_id": ciclo_id},
        )

        db.session.execute(
            text("""
                DELETE FROM ciclos_formativos
                WHERE id = :ciclo_id
            """),
            {"ciclo_id": ciclo_id},
        )

        db.session.commit()
        _delete_uploaded_files(urls_to_delete)
        flash("Ciclo formativo e todos os seus dados eliminados.", "success")

    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Error eliminando ciclo formativo: %s", e, exc_info=True)
        flash("Erro ao eliminar o ciclo formativo.", "danger")

    return redirect(url_for("admin.admin", tab="ciclos"))


# ──────────────────────────────────────────────
# DISCIPLINAS
# ──────────────────────────────────────────────

@admin_bp.route("/admin/disciplinas/create", methods=["POST"])
def create_disciplina():
    """
    Crea una disciplina dentro de un año de ciclo.
    También genera automáticamente sus secciones base.
    """
    try:
        ano_id = _to_int(request.form.get("ano_id"))
        nombre = request.form.get("nombre", "").strip()

        horas_raw = request.form.get("horas", "").strip()
        horas = int(horas_raw) if horas_raw else None

        if ano_id and nombre:
            result = db.session.execute(
                text("""
                    INSERT INTO disciplinas_ciclo
                    (ano_id, codigo, nombre, tipo, horas, descripcion, orden)
                    VALUES
                    (:ano_id, :codigo, :nombre, :tipo, :horas, :descripcion, :orden)
                """),
                {
                    "ano_id": ano_id,
                    "codigo": request.form.get("codigo", "").strip() or None,
                    "nombre": nombre,
                    "tipo": request.form.get("tipo", "disciplina").strip(),
                    "horas": horas,
                    "descripcion": request.form.get("descripcion", "").strip(),
                    "orden": _to_int(request.form.get("orden"), 999),
                },
            )

            disciplina_id = result.lastrowid

            if disciplina_id:
                secciones_base = [
                    (
                        "Información General",
                        "informacion-general",
                        "Presentación de la asignatura, criterios de evaluación, cronograma y contactos.",
                        1,
                    ),
                    (
                        "Contenidos",
                        "contenidos",
                        "Módulos, presentaciones, vídeos, lecturas y materiales de apoyo.",
                        2,
                    ),
                    (
                        "Evaluación",
                        "evaluacion",
                        "Pruebas, trabajos, foros, cuestionarios y criterios de evaluación.",
                        3,
                    ),
                    (
                        "Evidencias",
                        "evidencias",
                        "Portafolio, informes, trabajos y evidencias del aprendizaje.",
                        4,
                    ),
                    (
                        "Comunicación",
                        "comunicacion",
                        "Foro de avisos, foro de dudas y canales de contacto con el formador.",
                        5,
                    ),
                ]

                for titulo, slug, descripcion, orden in secciones_base:
                    db.session.execute(
                        text("""
                            INSERT INTO secciones_disciplina
                            (disciplina_id, titulo, slug, descripcion, orden, visible)
                            VALUES
                            (:disciplina_id, :titulo, :slug, :descripcion, :orden, 1)
                        """),
                        {
                            "disciplina_id": disciplina_id,
                            "titulo": titulo,
                            "slug": slug,
                            "descripcion": descripcion,
                            "orden": orden,
                        },
                    )

            db.session.commit()
            flash("Disciplina criada com as 5 secções base.", "success")
        else:
            flash("Faltam dados obrigatórios (ano de ciclo e nome).", "warning")

    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Error creando disciplina: %s", e, exc_info=True)
        flash("Erro ao criar a disciplina.", "danger")

    return redirect(url_for("admin.admin", tab="disciplinas"))


@admin_bp.route("/admin/disciplinas/<int:disciplina_id>/update", methods=["POST"])
def update_disciplina(disciplina_id):
    try:
        horas_raw = request.form.get("horas", "").strip()
        horas = int(horas_raw) if horas_raw else None

        db.session.execute(
            text("""
                UPDATE disciplinas_ciclo
                SET
                    codigo = :codigo,
                    nombre = :nombre,
                    tipo = :tipo,
                    horas = :horas,
                    descripcion = :descripcion
                WHERE id = :disciplina_id
            """),
            {
                "disciplina_id": disciplina_id,
                "codigo": request.form.get("codigo", "").strip(),
                "nombre": request.form.get("nombre", "").strip(),
                "tipo": request.form.get("tipo", "disciplina").strip(),
                "horas": horas,
                "descripcion": request.form.get("descripcion", "").strip(),
            },
        )
        db.session.commit()
        flash("Disciplina atualizada.", "success")

    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Error actualizando disciplina: %s", e, exc_info=True)
        flash("Erro ao atualizar a disciplina.", "danger")

    return redirect(url_for("admin.admin", tab="disciplinas"))


@admin_bp.route("/admin/disciplinas/<int:disciplina_id>/delete", methods=["POST"])
def delete_disciplina(disciplina_id):
    """
    Elimina una disciplina:
    recursos -> secciones -> disciplina.
    También borra los archivos físicos de los recursos asociados.
    """
    try:
        recursos = _fetch_all("""
            SELECT r.url
            FROM recursos_disciplina r
            JOIN secciones_disciplina s ON s.id = r.seccion_id
            WHERE s.disciplina_id = :disciplina_id
        """, {"disciplina_id": disciplina_id})

        urls_to_delete = [r["url"] for r in recursos if r.get("url")]

        db.session.execute(
            text("""
                DELETE r
                FROM recursos_disciplina r
                JOIN secciones_disciplina s ON s.id = r.seccion_id
                WHERE s.disciplina_id = :disciplina_id
            """),
            {"disciplina_id": disciplina_id},
        )

        db.session.execute(
            text("""
                DELETE FROM secciones_disciplina
                WHERE disciplina_id = :disciplina_id
            """),
            {"disciplina_id": disciplina_id},
        )

        db.session.execute(
            text("""
                DELETE FROM disciplinas_ciclo
                WHERE id = :disciplina_id
            """),
            {"disciplina_id": disciplina_id},
        )

        db.session.commit()
        _delete_uploaded_files(urls_to_delete)
        flash("Disciplina e as suas secções eliminadas.", "success")

    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Error eliminando disciplina: %s", e, exc_info=True)
        flash("Erro ao eliminar a disciplina.", "danger")

    return redirect(url_for("admin.admin", tab="disciplinas"))


# ──────────────────────────────────────────────
# SECCIONES DE DISCIPLINA
# ──────────────────────────────────────────────

@admin_bp.route("/admin/secciones/<int:seccion_id>/update", methods=["POST"])
def update_seccion(seccion_id):
    try:
        db.session.execute(
            text("""
                UPDATE secciones_disciplina
                SET
                    titulo = :titulo,
                    descripcion = :descripcion,
                    orden = :orden,
                    visible = :visible
                WHERE id = :seccion_id
            """),
            {
                "seccion_id": seccion_id,
                "titulo": request.form.get("titulo", "").strip(),
                "descripcion": request.form.get("descripcion", "").strip(),
                "orden": _to_int(request.form.get("orden"), 0),
                "visible": _checkbox_value("visible"),
            },
        )
        db.session.commit()
        flash("Secção atualizada.", "success")

    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Error actualizando sección de disciplina: %s", e, exc_info=True)
        flash("Erro ao atualizar a secção.", "danger")

    return redirect(url_for("admin.admin", tab="secciones"))


@admin_bp.route("/admin/secciones/<int:seccion_id>/toggle", methods=["POST"])
def toggle_seccion(seccion_id):
    try:
        db.session.execute(
            text("""
                UPDATE secciones_disciplina
                SET visible = CASE WHEN visible = 1 THEN 0 ELSE 1 END
                WHERE id = :seccion_id
            """),
            {"seccion_id": seccion_id},
        )
        db.session.commit()
        flash("Visibilidade da secção atualizada.", "info")

    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Error cambiando visibilidad de sección: %s", e, exc_info=True)
        flash("Erro ao alterar a visibilidade da secção.", "danger")

    return redirect(url_for("admin.admin", tab="secciones"))


@admin_bp.route("/admin/secciones/<int:seccion_id>/delete", methods=["POST"])
def delete_seccion(seccion_id):
    """
    Elimina una sección de disciplina y sus recursos.
    También borra los archivos físicos de los recursos asociados.
    """
    try:
        recursos = _fetch_all("""
            SELECT url
            FROM recursos_disciplina
            WHERE seccion_id = :seccion_id
        """, {"seccion_id": seccion_id})

        urls_to_delete = [r["url"] for r in recursos if r.get("url")]

        db.session.execute(
            text("""
                DELETE FROM recursos_disciplina
                WHERE seccion_id = :seccion_id
            """),
            {"seccion_id": seccion_id},
        )

        db.session.execute(
            text("""
                DELETE FROM secciones_disciplina
                WHERE id = :seccion_id
            """),
            {"seccion_id": seccion_id},
        )

        db.session.commit()
        _delete_uploaded_files(urls_to_delete)
        flash("Secção e os seus recursos eliminados.", "success")

    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Error eliminando sección de disciplina: %s", e, exc_info=True)
        flash("Erro ao eliminar a secção.", "danger")

    return redirect(url_for("admin.admin", tab="secciones"))


# ──────────────────────────────────────────────
# RECURSOS DE DISCIPLINA
# ──────────────────────────────────────────────

@admin_bp.route("/admin/recursos/create", methods=["POST"])
def create_recurso():
    try:
        seccion_id = _to_int(request.form.get("seccion_id"))
        titulo = request.form.get("titulo", "").strip()

        if seccion_id and titulo:
            uploaded_url = _save_uploaded_file("archivo", "recursos")
            url = uploaded_url or request.form.get("url", "").strip() or None

            data_limite_raw = request.form.get("data_limite", "").strip() or None
            db.session.execute(
                text("""
                    INSERT INTO recursos_disciplina
                    (seccion_id, titulo, tipo, descripcion, url, orden, visible, data_limite)
                    SELECT
                        :seccion_id,
                        :titulo,
                        :tipo,
                        :descripcion,
                        :url,
                        COALESCE(MAX(orden), 0) + 1,
                        1,
                        :data_limite
                    FROM recursos_disciplina
                    WHERE seccion_id = :seccion_id
                """),
                {
                    "seccion_id":  seccion_id,
                    "titulo":      titulo,
                    "tipo":        request.form.get("tipo", "documento").strip(),
                    "descripcion": request.form.get("descripcion", "").strip(),
                    "url":         url,
                    "data_limite": data_limite_raw,
                },
            )
            db.session.commit()
            flash("Recurso criado com sucesso.", "success")
        else:
            flash("Faltam dados obrigatórios (secção e título).", "warning")

    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Error creando recurso de disciplina: %s", e, exc_info=True)
        flash("Erro ao criar o recurso.", "danger")

    return redirect(url_for("admin.admin", tab="recursos"))


@admin_bp.route("/admin/recursos/<int:recurso_id>/update", methods=["POST"])
def update_recurso(recurso_id):
    try:
        recurso = _fetch_one("""
            SELECT url
            FROM recursos_disciplina
            WHERE id = :recurso_id
            LIMIT 1
        """, {"recurso_id": recurso_id})

        old_url = recurso["url"] if recurso else None

        uploaded_url = _save_uploaded_file("archivo", "recursos")
        url = uploaded_url or request.form.get("url", "").strip() or None

        data_limite_raw = request.form.get("data_limite", "").strip() or None
        db.session.execute(
            text("""
                UPDATE recursos_disciplina
                SET
                    titulo      = :titulo,
                    tipo        = :tipo,
                    descripcion = :descripcion,
                    url         = :url,
                    orden       = :orden,
                    visible     = :visible,
                    data_limite = :data_limite
                WHERE id = :recurso_id
            """),
            {
                "recurso_id":  recurso_id,
                "titulo":      request.form.get("titulo", "").strip(),
                "tipo":        request.form.get("tipo", "documento").strip(),
                "descripcion": request.form.get("descripcion", "").strip(),
                "url":         url,
                "orden":       _to_int(request.form.get("orden"), 0),
                "visible":     _checkbox_value("visible"),
                "data_limite": data_limite_raw,
            },
        )
        db.session.commit()

        if uploaded_url and old_url:
            _delete_uploaded_file(old_url)

        flash("Recurso atualizado com sucesso.", "success")

    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Error actualizando recurso de disciplina: %s", e, exc_info=True)
        flash("Erro ao atualizar o recurso.", "danger")

    return redirect(url_for("admin.admin", tab="recursos"))


@admin_bp.route("/admin/recursos/<int:recurso_id>/toggle", methods=["POST"])
def toggle_recurso(recurso_id):
    try:
        db.session.execute(
            text("""
                UPDATE recursos_disciplina
                SET visible = CASE WHEN visible = 1 THEN 0 ELSE 1 END
                WHERE id = :recurso_id
            """),
            {"recurso_id": recurso_id},
        )
        db.session.commit()
        flash("Visibilidade do recurso atualizada.", "info")

    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Error cambiando visibilidad del recurso: %s", e, exc_info=True)
        flash("Erro ao alterar a visibilidade do recurso.", "danger")

    return redirect(url_for("admin.admin", tab="recursos"))


@admin_bp.route("/admin/recursos/<int:recurso_id>/delete", methods=["POST"])
def delete_recurso(recurso_id):
    try:
        recurso = _fetch_one("""
            SELECT url
            FROM recursos_disciplina
            WHERE id = :recurso_id
            LIMIT 1
        """, {"recurso_id": recurso_id})

        old_url = recurso["url"] if recurso else None

        db.session.execute(
            text("""
                DELETE FROM recursos_disciplina
                WHERE id = :recurso_id
            """),
            {"recurso_id": recurso_id},
        )
        db.session.commit()

        _delete_uploaded_file(old_url)
        flash("Recurso eliminado com sucesso.", "success")

    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Error eliminando recurso de disciplina: %s", e, exc_info=True)
        flash("Erro ao eliminar o recurso.", "danger")

    return redirect(url_for("admin.admin", tab="recursos"))


# ──────────────────────────────────────────────
# CLASSIFICAÇÕES
# ──────────────────────────────────────────────

@admin_bp.route("/admin/classificacoes/nova", methods=["POST"])
def create_classificacao():
    try:
        usuario_id = _to_int(request.form.get("usuario_id"))
        disciplina = request.form.get("disciplina", "").strip()
        tipo_avaliacao = request.form.get("tipo_avaliacao", "").strip()
        nota_raw = request.form.get("nota", "").strip()
        observacao = request.form.get("observacao", "").strip()

        nota = None
        if nota_raw:
            nota = float(nota_raw)
            if nota < 0 or nota > 20:
                flash("A nota deve estar entre 0 e 20.", "warning")
                return redirect(url_for("admin.admin", tab="avaliacoes"))

        if usuario_id and disciplina and tipo_avaliacao:
            db.session.execute(
                text("""
                    INSERT INTO classificacoes
                    (usuario_id, disciplina, tipo_avaliacao, nota, observacao, data_avaliacao, criado_em)
                    VALUES
                    (:usuario_id, :disciplina, :tipo_avaliacao, :nota, :observacao, CURDATE(), NOW())
                """),
                {
                    "usuario_id": usuario_id,
                    "disciplina": disciplina,
                    "tipo_avaliacao": tipo_avaliacao,
                    "nota": nota,
                    "observacao": observacao or None,
                },
            )
            db.session.commit()
            flash("Classificação registada com sucesso.", "success")
        else:
            flash("Faltam dados obrigatórios (aluno, disciplina e tipo de avaliação).", "warning")

    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Error creando clasificación: %s", e, exc_info=True)
        flash("Erro ao registar a classificação.", "danger")

    return redirect(url_for("admin.admin", tab="avaliacoes"))


# ──────────────────────────────────────────────
# ATIVIDADE (admin view)
# ──────────────────────────────────────────────

@admin_bp.route("/admin/atividade")
def admin_atividade():
    usuario = get_current_user()
    logs = _fetch_all("""
        SELECT
            al.id,
            al.tipo,
            al.created_at,
            al.usuario_id,
            al.recurso_id,
            u.nome        AS aluno_nome,
            u.username    AS aluno_username,
            r.titulo      AS recurso_titulo,
            d.nombre      AS disciplina_nome
        FROM activity_log al
        LEFT JOIN usuarios u ON u.id = al.usuario_id
        LEFT JOIN recursos_disciplina r ON r.id = al.recurso_id
        LEFT JOIN secciones_disciplina s ON s.id = r.seccion_id
        LEFT JOIN disciplinas_ciclo d ON d.id = s.disciplina_id
        ORDER BY al.created_at DESC
        LIMIT 500
    """)
    return render_template("admin_atividade.html", usuario=usuario, logs=logs)


# ──────────────────────────────────────────────
# QUIZ BUILDER (admin)
# ──────────────────────────────────────────────

def _get_or_create_questionario(recurso):
    """Questionário associado ao recurso; cria-o se ainda não existir."""
    q = _fetch_one(
        "SELECT id, titulo, descricao FROM questionarios WHERE recurso_id = :r",
        {"r": recurso["id"]},
    )
    if q:
        return q
    try:
        db.session.execute(
            text("""INSERT INTO questionarios (recurso_id, titulo)
                    VALUES (:r, :titulo)"""),
            {"r": recurso["id"], "titulo": recurso["titulo"]},
        )
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error("[admin] criar questionario: %s", e, exc_info=True)
        return None
    return _fetch_one(
        "SELECT id, titulo, descricao FROM questionarios WHERE recurso_id = :r",
        {"r": recurso["id"]},
    )


@admin_bp.route("/admin/quiz/<int:recurso_id>")
def admin_quiz(recurso_id):
    usuario = get_current_user()

    recurso = _fetch_one(
        """SELECT r.id, r.titulo, d.nombre AS disciplina_nome
           FROM recursos_disciplina r
           LEFT JOIN secciones_disciplina s ON s.id = r.seccion_id
           LEFT JOIN disciplinas_ciclo d ON d.id = s.disciplina_id
           WHERE r.id = :r""",
        {"r": recurso_id},
    )
    if not recurso:
        abort(404)

    questionario = _get_or_create_questionario(recurso)
    if not questionario:
        flash("Erro ao preparar o questionário.", "danger")
        return redirect(url_for("admin.admin", tab="recursos"))

    perguntas = _fetch_all(
        """SELECT id, enunciado, tipo, ordem FROM perguntas
           WHERE questionario_id = :q ORDER BY ordem ASC, id ASC""",
        {"q": questionario["id"]},
    )
    opcoes = _fetch_all(
        """SELECT o.id, o.pergunta_id, o.texto, o.correta
           FROM opcoes_resposta o
           JOIN perguntas p ON p.id = o.pergunta_id
           WHERE p.questionario_id = :q
           ORDER BY o.id ASC""",
        {"q": questionario["id"]},
    )
    opcoes_por_pergunta = {}
    for o in opcoes:
        opcoes_por_pergunta.setdefault(o["pergunta_id"], []).append(o)

    n_tentativas = _fetch_one(
        "SELECT COUNT(*) AS n FROM tentativas_quiz WHERE questionario_id = :q",
        {"q": questionario["id"]},
    )

    return render_template(
        "admin_quiz.html",
        usuario=usuario,
        recurso=recurso,
        questionario=questionario,
        perguntas=perguntas,
        opcoes_por_pergunta=opcoes_por_pergunta,
        n_tentativas=(n_tentativas["n"] if n_tentativas else 0) or 0,
    )


@admin_bp.route("/admin/quiz/<int:recurso_id>/meta", methods=["POST"])
def admin_quiz_meta(recurso_id):
    titulo = (request.form.get("titulo") or "").strip()
    descricao = (request.form.get("descricao") or "").strip()
    if not titulo:
        flash("O título é obrigatório.", "warning")
        return redirect(url_for("admin.admin_quiz", recurso_id=recurso_id))
    try:
        db.session.execute(
            text("""UPDATE questionarios SET titulo = :t, descricao = :d
                    WHERE recurso_id = :r"""),
            {"t": titulo, "d": descricao or None, "r": recurso_id},
        )
        db.session.commit()
        flash("Questionário atualizado.", "success")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error("[admin] quiz_meta: %s", e, exc_info=True)
        flash("Erro ao atualizar o questionário.", "danger")
    return redirect(url_for("admin.admin_quiz", recurso_id=recurso_id))


@admin_bp.route("/admin/quiz/<int:recurso_id>/pergunta/create", methods=["POST"])
def admin_quiz_pergunta_create(recurso_id):
    questionario = _fetch_one(
        "SELECT id FROM questionarios WHERE recurso_id = :r", {"r": recurso_id}
    )
    if not questionario:
        abort(404)

    enunciado = (request.form.get("enunciado") or "").strip()
    correta_idx = request.form.get("correta", type=int)
    opcoes = []
    for i in range(1, 5):
        texto = (request.form.get(f"opcao_{i}") or "").strip()
        if texto:
            opcoes.append((i, texto))

    if not enunciado or len(opcoes) < 2 or correta_idx not in [i for i, _ in opcoes]:
        flash("Preenche o enunciado, pelo menos 2 opções e marca a correta.", "warning")
        return redirect(url_for("admin.admin_quiz", recurso_id=recurso_id))

    try:
        ordem_row = _fetch_one(
            "SELECT COALESCE(MAX(ordem), 0) + 1 AS prox FROM perguntas WHERE questionario_id = :q",
            {"q": questionario["id"]},
        )
        result = db.session.execute(
            text("""INSERT INTO perguntas (questionario_id, enunciado, ordem)
                    VALUES (:q, :e, :o)"""),
            {"q": questionario["id"], "e": enunciado,
             "o": (ordem_row["prox"] if ordem_row else 1) or 1},
        )
        pergunta_id = result.lastrowid
        for i, texto in opcoes:
            db.session.execute(
                text("""INSERT INTO opcoes_resposta (pergunta_id, texto, correta)
                        VALUES (:p, :t, :c)"""),
                {"p": pergunta_id, "t": texto, "c": 1 if i == correta_idx else 0},
            )
        db.session.commit()
        flash("Pergunta adicionada.", "success")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error("[admin] quiz_pergunta_create: %s", e, exc_info=True)
        flash("Erro ao adicionar a pergunta.", "danger")
    return redirect(url_for("admin.admin_quiz", recurso_id=recurso_id))


@admin_bp.route("/admin/quiz/<int:recurso_id>/pergunta/<int:pergunta_id>/delete", methods=["POST"])
def admin_quiz_pergunta_delete(recurso_id, pergunta_id):
    try:
        db.session.execute(
            text("DELETE FROM respostas_aluno WHERE pergunta_id = :p"), {"p": pergunta_id}
        )
        db.session.execute(
            text("DELETE FROM opcoes_resposta WHERE pergunta_id = :p"), {"p": pergunta_id}
        )
        db.session.execute(
            text("DELETE FROM perguntas WHERE id = :p"), {"p": pergunta_id}
        )
        db.session.commit()
        flash("Pergunta eliminada.", "success")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error("[admin] quiz_pergunta_delete: %s", e, exc_info=True)
        flash("Erro ao eliminar a pergunta.", "danger")
    return redirect(url_for("admin.admin_quiz", recurso_id=recurso_id))


# ──────────────────────────────────────────────
# ENTREGAS (admin view)
# ──────────────────────────────────────────────

@admin_bp.route("/admin/entregas")
def admin_entregas():
    usuario = get_current_user()

    entregas = _fetch_all("""
        SELECT
            e.id,
            e.estado,
            e.ficheiro_url,
            e.nota,
            e.feedback,
            e.data_entrega,
            e.data_avaliacao,
            e.usuario_id,
            e.recurso_id,
            u.nome        AS aluno_nome,
            u.username    AS aluno_username,
            r.titulo      AS recurso_titulo,
            d.nombre      AS disciplina_nome
        FROM entregas e
        LEFT JOIN usuarios u ON u.id = e.usuario_id
        LEFT JOIN recursos_disciplina r ON r.id = e.recurso_id
        LEFT JOIN secciones_disciplina s ON s.id = r.seccion_id
        LEFT JOIN disciplinas_ciclo d ON d.id = s.disciplina_id
        ORDER BY e.data_entrega DESC
        LIMIT 500
    """)

    return render_template(
        "admin_entregas.html",
        usuario=usuario,
        entregas=entregas,
    )


@admin_bp.route("/admin/entregas/<int:entrega_id>/nota", methods=["POST"])
def admin_nota_entrega(entrega_id):
    try:
        nota_raw = request.form.get("nota", "").strip()
        estado   = request.form.get("estado", "entregue").strip()
        feedback = request.form.get("feedback", "").strip() or None

        nota = None
        if nota_raw:
            nota = float(nota_raw)

        db.session.execute(
            text("""
                UPDATE entregas
                SET nota             = :nota,
                    estado           = :estado,
                    feedback         = :feedback,
                    data_avaliacao   = CASE WHEN :avaliado THEN NOW() ELSE data_avaliacao END
                WHERE id = :id
            """),
            {
                "nota":     nota,
                "estado":   estado,
                "feedback": feedback,
                "avaliado": estado == "avaliado",
                "id":       entrega_id,
            },
        )
        db.session.commit()
        flash("Nota atualizada.", "success")

        if estado == "avaliado" and nota is not None:
            _enviar_email_nota(entrega_id, nota, feedback)

    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Error actualizando nota de entrega: %s", e, exc_info=True)
        flash("Erro ao atualizar a nota.", "danger")

    return redirect(url_for("admin.admin_entregas"))


def _enviar_email_nota(entrega_id, nota, feedback=None):
    try:
        row = db.session.execute(
            text("""
                SELECT u.email, u.nome, r.titulo AS recurso_titulo
                FROM entregas e
                JOIN usuarios u ON u.id = e.usuario_id
                LEFT JOIN recursos_disciplina r ON r.id = e.recurso_id
                WHERE e.id = :id
            """),
            {"id": entrega_id},
        ).mappings().first()

        if not row or not row["email"]:
            return

        nome   = row["nome"] or "Aluno"
        titulo = row["recurso_titulo"] or "Tarefa"
        cor    = "#059669" if nota >= 10 else "#dc2626"
        estado_texto = "positiva" if nota >= 10 else "negativa"

        html = f"""
        <div style="font-family:sans-serif;max-width:520px;margin:0 auto;color:#1a1a2e">
          <div style="background:#1a1a2e;padding:20px 24px;border-radius:8px 8px 0 0">
            <h2 style="color:#fff;margin:0;font-size:18px">Academia Profissional</h2>
            <p style="color:#94a3b8;margin:4px 0 0;font-size:12px">Campus Virtual</p>
          </div>
          <div style="background:#f8fafc;padding:24px;border-radius:0 0 8px 8px;border:1px solid #e2e8f0">
            <p style="margin:0 0 16px">Olá <strong>{nome}</strong>,</p>
            <p style="margin:0 0 16px">A tua entrega foi avaliada:</p>
            <div style="background:#fff;border:1px solid #e2e8f0;border-radius:6px;padding:16px;margin-bottom:16px">
              <p style="margin:0 0 6px;font-size:13px;color:#64748b">Tarefa</p>
              <p style="margin:0 0 12px;font-weight:700">{titulo}</p>
              <p style="margin:0 0 6px;font-size:13px;color:#64748b">Nota</p>
              <p style="margin:0 0 {'16px' if feedback else '0'};font-size:28px;font-weight:800;color:{cor}">{nota}/20
                <span style="font-size:13px;font-weight:400;color:#64748b">— classificação {estado_texto}</span>
              </p>
              {f'<p style="margin:0 0 6px;font-size:13px;color:#64748b">Comentário do professor</p><p style="margin:0;font-size:13px;line-height:1.6">{feedback}</p>' if feedback else ''}
            </div>
            <a href="/as-minhas-entregas"
               style="display:inline-block;background:#1a1a2e;color:#fff;padding:10px 20px;
                      border-radius:6px;text-decoration:none;font-size:13px">
              Ver todas as minhas entregas
            </a>
            <p style="margin:20px 0 0;font-size:11px;color:#94a3b8">
              Campus Virtual — Academia Profissional Prof. Albino de Matos
            </p>
          </div>
        </div>
        """

        msg = Message(
            subject=f"Nota disponível: {titulo}",
            recipients=[row["email"]],
            html=html,
        )
        mail.send(msg)
        current_app.logger.info("[mail] nota enviada a %s (entrega %s)", row["email"], entrega_id)

    except Exception as e:
        current_app.logger.warning("[mail] falhou ao enviar nota entrega %s: %s", entrega_id, e)

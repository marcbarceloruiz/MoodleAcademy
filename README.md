# MoodleAcademy — Campus Virtual

**Academia Profissional Prof. Albino de Matos · Escola Profissional Vértice**

Campus virtual tipo Moodle construido con Flask + MySQL/MariaDB.  
Gestiona ciclos formativos, disciplinas, secciones, recursos y documentos institucionales desde un panel de administración protegido.

---

## Tecnologías

| Capa | Tecnología |
|------|-----------|
| Backend | Python 3.x + Flask |
| Base de datos | MySQL / MariaDB + SQLAlchemy + Flask-Migrate |
| Frontend | HTML5 + CSS3 (sin frameworks externos) |
| Seguridad | Werkzeug password hashing (scrypt) |

---

## Estructura del proyecto

```
MoodleAcademy/
├── app.py                         # Punto de entrada Flask
├── config.py                      # Configuración (lee .env)
├── decorators.py                  # @login_required, @role_required
├── extensions.py                  # db, migrate
├── models/                        # SQLAlchemy models
├── routes/
│   ├── admin_routes.py            # Panel admin (/admin)  ← no tocar
│   ├── auth_routes.py             # Login/logout (/login, /logout)
│   ├── courses_routes.py          # Ciclos y disciplinas
│   ├── dashboard_routes.py        # Dashboard principal
│   └── portal_routes.py           # Portal institucional
├── services/
│   └── data_service.py            # Capa de acceso a datos
├── templates/
│   ├── partials/
│   │   ├── topbar.html            # Cabecera con auth
│   │   ├── sidebar.html           # Navegación lateral
│   │   └── flash_messages.html    # Mensajes flash
│   ├── login.html                 # Formulario de login
│   ├── 403.html                   # Acceso denegado
│   ├── 404.html                   # No encontrado
│   └── ...
├── static/
│   ├── css/
│   │   ├── components.css         # Botones, cards, modales, toasts
│   │   └── responsive.css         # Media queries
│   ├── js/
│   │   └── main.js                # Modales, toasts, sidebar toggle
│   └── uploads/                   # Archivos subidos (no en git)
└── sql/
    ├── seed_estrutura_extra.sql         # CREATE TABLE IF NOT EXISTS (auth)
    ├── seed_roles.sql                   # INSERT roles base
    ├── seed_usuarios_demo.sql           # INSERT usuarios demo
    ├── seed_portal_estrutura_extra.sql  # INSERT áreas portal (CTEs, EFA…)
    └── diagnostico_duplicados.sql       # SELECT diagnóstico (no modifica)
```

---

## Instalación

```bash
# 1. Crear y activar entorno virtual
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar .env
cp .env.example .env           # rellenar los valores

# 4. Ejecutar migraciones de BD
flask db upgrade

# 5. Arrancar
python app.py
```

---

## Variables de entorno (.env)

```env
DATABASE_URL=mysql+pymysql://usuario:password@localhost/nombre_db
SECRET_KEY=cambia_esto_por_algo_aleatorio_y_largo
ADMIN_PASSWORD=password_para_admin_legacy
FLASK_DEBUG=True
```

---

## Sistema de autenticación

### Dos sistemas que conviven sin conflicto

| Sistema | Ruta login | Sesión | Uso |
|---------|-----------|--------|-----|
| **Legacy admin** | `/admin/login` | `session["admin_ok"] = True` | `ADMIN_PASSWORD` del `.env` |
| **Nuevo (roles)** | `/login` | `session["usuario_id"]` + `session["usuario_roles"]` | Tabla `usuarios` + `roles` en BD |

- El login legacy (`/admin/login`) sigue funcionando con `ADMIN_PASSWORD`.  
- El login nuevo (`/login`) usa usuarios de la tabla `usuarios` con contraseñas hashadas.
- Ambos sistemas **conviven**: un admin del nuevo sistema también tiene `admin_ok = True`.
- El logout (`/logout`) limpia **ambos** sistemas a la vez.
- El logout legacy (`/admin/logout`) también limpia ambos por seguridad.

### Roles del nuevo sistema

| Role | Acceso |
|------|--------|
| `admin` | Todo, incluyendo panel `/admin` |
| `docente` | Área Docente, Manual do Formador |
| `aluno` | Dashboard, ciclos, portal público |

### Variables de sesión disponibles en templates

```jinja
session_autenticado      {# bool #}
session_is_admin         {# bool #}
session_is_docente       {# bool #}
session_is_aluno         {# bool #}
session_usuario_nome     {# str  #}
session_usuario_username {# str  #}
session_roles            {# list #}
```

---

## SQL Seeds — Orden de ejecución en phpMyAdmin

Ejecutar **en este orden exacto**:

```
1. sql/seed_estrutura_extra.sql         ← Crea tablas usuarios, roles, usuario_roles
2. sql/seed_roles.sql                   ← Inserta roles: admin, docente, aluno
3. sql/seed_usuarios_demo.sql           ← Inserta 3 usuarios de demo
4. sql/seed_portal_estrutura_extra.sql  ← Inserta áreas CTEs, EFA, FMC en el portal
```

Diagnóstico (solo lectura, no modifica nada):
```
   sql/diagnostico_duplicados.sql
```

Todos los seeds son **re-ejecutables**: usan `INSERT ... WHERE NOT EXISTS` o `INSERT IGNORE`.

---

## Usuarios demo

Disponibles tras ejecutar los SQL seeds 1-3:

| Usuario | Contraseña | Role |
|---------|------------|------|
| `admin` | `admin123` | admin |
| `docente` | `docente123` | docente |
| `aluno` | `aluno123` | aluno |

Las contraseñas están hashadas con `werkzeug.security.generate_password_hash` (scrypt).  
**Cambiar en producción** antes de desplegar.

---

## URLs principales

| URL | Descripción | Acceso |
|-----|-------------|--------|
| `/` | Dashboard | Público |
| `/login` | Login nuevo sistema | Público |
| `/logout` | Logout (POST) | Autenticado |
| `/ciclos` | Ciclos formativos | Público |
| `/ciclos/<id>` | Detalle de ciclo | Público |
| `/portal` | Portal institucional | Público |
| `/portal/erasmus` | Área Erasmus+ | Público |
| `/portal/area-docente` | Área Docente | docente / admin |
| `/portal/manual-formador` | Manual do Formador | docente / admin |
| `/admin/login` | Login legacy (ADMIN_PASSWORD) | Público |
| `/admin` | Panel de administración | admin |
| `/acesso-negado` | Página 403 | Público |

---

## Funcionalidades demo / futura integración

Las siguientes funcionalidades **muestran un aviso** de futura integración al activarlas:

- **Editar perfil** — modal de perfil de usuario
- **Alterar palavra-passe** — modal de perfil de usuario
- **Notificações** — icono de campana en la topbar

Estas funcionalidades están preparadas en el frontend (botones visibles) pero no tienen backend implementado. El mensaje mostrado es:  
*"Funcionalidade preparada para futura integração."*

---

## Notas de arquitectura

- **`admin_routes.py`** — No modificar la lógica de `before_request` ni el login legacy. Los cambios al sistema de auth van en `auth_routes.py` y `decorators.py`.
- **`data_service.py`** — Siempre intenta MySQL primero; si falla o no hay datos, usa fallback de `mock_data`.  
- **Portal** — Las áreas del portal se sirven desde MySQL (`areas_institucionais`). Si un slug no está en BD pero sí en `AREA_UI` del código, se muestra con datos de fallback.
- **`static/uploads/`** — No incluir en git. Los archivos subidos desde el admin se guardan aquí.

# MoodleAcademy — Campus Virtual

**Academia Profissional Prof. Albino de Matos · Escola Profissional Vértice**

Campus virtual tipo Moodle construido con Flask + MySQL/MariaDB. Permite gestionar ciclos formativos, disciplinas, secciones, recursos y documentos institucionales desde un panel de administración protegido por contraseña.

---

## Tecnologías usadas

| Capa | Tecnología |
|---|---|
| Backend | Python 3.10+, Flask 3.x |
| ORM | Flask-SQLAlchemy 3.x + SQLAlchemy 2.x |
| Migraciones | Flask-Migrate (Alembic) |
| Base de datos | MySQL 8 / MariaDB 10.6+ |
| Driver MySQL | PyMySQL |
| Templates | Jinja2 |
| Frontend | HTML5, CSS3 modular, JavaScript mínimo |
| Servidor prod. | Gunicorn |
| Gestión .env | python-dotenv |

---

## Estructura de carpetas

```
MoodleAcademy/
├── app.py                          # Punto de entrada Flask (create_app)
├── config.py                       # Configuración: DB, SECRET_KEY, uploads, debug
├── extensions.py                   # db = SQLAlchemy(), migrate = Migrate()
├── requirements.txt                # Dependencias pip
├── README.md
│
├── routes/
│   ├── admin_routes.py             # /admin — Panel de administración
│   ├── portal_routes.py            # /portal — Portal institucional público
│   ├── courses_routes.py           # /ciclos, /ciclos/<slug> — Ciclos formativos
│   └── dashboard_routes.py         # / — Dashboard del alumno
│
├── services/
│   └── data_service.py             # Lógica de negocio y acceso a datos
│
├── models/
│   ├── area_moodle.py
│   ├── centro.py
│   ├── ciclo_formativo.py
│   └── modulo_actividad.py
│
├── templates/
│   ├── base.html                   # Layout principal (topbar, sidebar, flash)
│   ├── admin.html                  # Panel admin con pestañas
│   ├── admin_login.html            # Login del admin
│   ├── portal.html                 # Portal institucional
│   ├── ciclos.html                 # Lista de ciclos formativos
│   ├── ciclo_detail.html           # Detalle de ciclo
│   ├── disciplina_detail.html      # Detalle de disciplina con recursos
│   └── partials/
│       ├── flash_messages.html     # Mensajes flash (éxito/error/info)
│       ├── topbar.html
│       ├── sidebar.html
│       └── modal.html
│
├── static/
│   ├── css/
│   │   ├── base.css                # Variables CSS y reset
│   │   ├── layout.css              # Grid, sidebar, topbar
│   │   ├── components.css          # Botones, tablas, toasts, badges
│   │   ├── admin.css               # Estilos específicos del admin
│   │   └── ...
│   ├── js/
│   │   └── main.js                 # JS ligero (modales, tabs, etc.)
│   ├── img/
│   │   └── logo-appam.png
│   └── uploads/                    # ⚠️ NO subir a Git (ver advertencias)
│       ├── documentos/             # PDFs de documentos institucionales
│       └── recursos/               # Archivos de recursos de disciplinas
│
└── data/
    └── mock_data.py                # Datos simulados para sidebar/dashboard
```

---

## Variables necesarias en `.env`

Crea el archivo `.env` en la raíz del proyecto (nunca lo subas a Git):

```env
# Clave de sesiones Flask — CAMBIA ESTO en producción
SECRET_KEY=cambia-esto-por-algo-seguro

# Cadena de conexión MySQL/MariaDB
DATABASE_URL=mysql+pymysql://usuario:contraseña@127.0.0.1:3306/academia_profissional_albino_matos

# Modo desarrollo (True activa debug y recarga automática)
FLASK_DEBUG=True

# Contraseña del panel de administración
ADMIN_PASSWORD=tu_contraseña_segura
```

> Puedes partir de `.env.example` ya incluido en el repositorio.

---

## Cómo instalar dependencias

### Windows

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Cómo arrancar Flask

```bash
# Modo desarrollo (con recarga automática)
python app.py

# Alternativa con Flask CLI
flask run --debug
```

Abre en el navegador: `http://127.0.0.1:5000`

### Producción con Gunicorn (Linux)

```bash
gunicorn -w 4 -b 0.0.0.0:8000 "app:app"
```

---

## Cómo acceder al panel admin

1. Ve a `http://127.0.0.1:5000/admin`
2. Introduce la contraseña definida en `ADMIN_PASSWORD` del `.env`
3. La sesión es válida hasta que cierres el navegador o hagas logout

---

## Funcionalidades actuales

### Portal institucional (`/portal`)
- Muestra áreas institucionales con sus documentos asociados
- Abre PDFs y archivos subidos directamente en el navegador

### Panel de administración (`/admin`)
Protegido con contraseña. Pestañas disponibles:

| Pestaña | Qué permite |
|---|---|
| **Portal** | Editar áreas institucionales (título, descripción, contenido, visibilidad) |
| **Documentos** | Crear, editar, ocultar/mostrar, eliminar documentos; subir PDFs |
| **Ciclos** | Crear ciclos formativos (genera 3 años automáticamente), editar, eliminar |
| **Disciplinas** | Crear disciplinas (genera 5 secciones base), editar, eliminar |
| **Secciones** | Editar, ocultar/mostrar y eliminar secciones de disciplinas |
| **Recursos** | Crear, editar, ocultar/mostrar, eliminar recursos; subir archivos |

- Al borrar documentos o recursos, el archivo físico se elimina de `static/uploads/`
- Todas las operaciones muestran **mensajes flash** de éxito, aviso o error
- Los mensajes desaparecen automáticamente tras 5 segundos (clic para cerrar)

### Ciclos y disciplinas (`/ciclos`, `/ciclos/<slug>`)
- Listado de ciclos formativos activos
- Detalle con años y disciplinas
- Vista de disciplina con secciones y recursos descargables

### Dashboard (`/`)
- Vista principal del alumno con datos de cursos y eventos (datos simulados)

---

## Funcionalidades pendientes

| Funcionalidad | Estado |
|---|---|
| Login real con usuarios en DB | Pendiente |
| Roles y permisos (alumno / profesor / admin) | Pendiente |
| Registro y gestión de alumnos | Pendiente |
| Matrícula en ciclos / disciplinas | Pendiente |
| Entrega de tareas con corrección | Pendiente |
| Cuestionarios con puntuación | Pendiente |
| Mensajería interna | Pendiente |
| Notificaciones push / email | Pendiente |
| Calendario interactivo | Pendiente |
| Exportación de calificaciones | Pendiente |
| Foros por disciplina | Pendiente |
| Panel de estadísticas avanzado | Pendiente |
| Tests automatizados | Pendiente |
| Internacionalización (PT/ES) | Pendiente |

---

## ⚠️ Advertencias importantes

### No subas nunca a Git

```
.env                    ← contraseñas y claves
static/uploads/         ← archivos subidos por usuarios (pueden ser grandes o sensibles)
venv/                   ← entorno virtual (se regenera con pip install)
```

Asegúrate de que tu `.gitignore` incluye estas líneas:

```gitignore
.env
static/uploads/
venv/
__pycache__/
*.pyc
```

### SECRET\_KEY en producción

Cambia `SECRET_KEY` a un valor largo y aleatorio. Puedes generar uno con:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### ADMIN\_PASSWORD en producción

Usa una contraseña robusta. El sistema actual usa comparación directa de texto; no hay hash. Considera añadir hashing (bcrypt) en el futuro.

---

## Comandos Git recomendados

```bash
# Clonar el repositorio
git clone <url-del-repositorio>
cd MoodleAcademy

# Ver estado actual
git status

# Añadir cambios (nunca uses git add . sin revisar qué incluyes)
git add routes/admin_routes.py
git add templates/partials/flash_messages.html
git add static/css/components.css
git add README.md

# Commit con mensaje descriptivo
git commit -m "feat: añadir flash messages en operaciones del admin"

# Subir al remoto
git push origin main

# Ver historial compacto
git log --oneline -10

# Crear rama para nueva funcionalidad
git checkout -b feature/login-real

# Volver a main
git checkout main
```

---

## Convenciones de commits

```
feat:     nueva funcionalidad
fix:      corrección de bug
style:    cambios de CSS/HTML sin afectar lógica
refactor: reorganización sin cambiar comportamiento
docs:     cambios en documentación
chore:    cambios de configuración o dependencias
```

---

*Academia Profissional Prof. Albino de Matos · Escola Profissional Vértice — Campus Virtual*

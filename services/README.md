# Academia Vertice — Campus Virtual

Plataforma de formación online tipo Moodle construida con Flask + Jinja2.

---

## Descripción

Campus virtual de Academia Vertice. Permite a alumnos y profesores acceder a cursos, módulos, actividades, calendario, avisos y administración desde una interfaz web moderna renderizada en servidor con Flask y Jinja2.

---

## Instalación

### Requisitos

- Python 3.10 o superior
- pip

### Pasos en Windows

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Después abre en el navegador:

```txt
http://127.0.0.1:5000
```

### Pasos en Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

---

## Estructura del proyecto

```txt
academia-vertice-campus/
├── app.py                    # Punto de entrada Flask
├── config.py                 # Configuración
├── requirements.txt
├── README.md
├── data/
│   └── mock_data.py          # Datos simulados
├── services/
│   └── data_service.py       # Capa de servicio
├── routes/
│   ├── dashboard_routes.py   # /
│   ├── courses_routes.py     # /cursos, /cursos/<id>
│   ├── admin_routes.py       # /admin
│   └── portal_routes.py      # /portal
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── courses.html
│   ├── course_detail.html
│   ├── admin.html
│   ├── portal.html
│   └── partials/
└── static/
    ├── css/
    └── js/main.js
```

---

## Qué está simulado

- Usuario actual: Natachinha
- Cursos, módulos y actividades
- Alumnos, profesores, eventos y avisos
- Estadísticas de administración
- Progreso calculado desde Python
- Modales, toasts y acciones visuales sin persistencia real

---

## Qué queda pendiente

| Funcionalidad | Estado |
|---|---|
| Base de datos SQL | Pendiente |
| Login real | Pendiente |
| Roles y permisos | Pendiente |
| CRUD real de cursos | Pendiente |
| Entrega real de tareas | Pendiente |
| Tests con puntuación real | Pendiente |
| Mensajería interna | Pendiente |
| Notificaciones | Pendiente |
| Calendario interactivo | Pendiente |
| Exportación de notas | Pendiente |

---

## Tecnologías usadas

- Python
- Flask
- Jinja2
- HTML5
- CSS3 modular
- JavaScript mínimo

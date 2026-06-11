# Campus Virtual — Academia Profissional Prof. Albino de Matos
### Escola Profissional Vértice

Campus virtual tipo Moodle construído com **Flask + MySQL/MariaDB**, com autenticação por roles, portal institucional, ciclos formativos, disciplinas com estrutura pedagógica completa, matrículas, classificações, tarefas, calendário e notificações.

---

## Tecnologias

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.10+, Flask 3.x |
| ORM / SQL | Flask-SQLAlchemy + SQL direto (PyMySQL) |
| Base de dados | MySQL 8 / MariaDB 10.6+ (XAMPP) |
| Templates | Jinja2 |
| Frontend | HTML5, CSS modular, JS vanilla |
| Autenticação | Sessões Flask + hash werkzeug (pbkdf2:sha256) |

---

## Instalação

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Variáveis de ambiente (.env)

```env
SECRET_KEY=valor-longo-e-aleatorio
DATABASE_URL=mysql+pymysql://root:@127.0.0.1:3306/academia_profissional_albino_matos
FLASK_DEBUG=True
ADMIN_PASSWORD=admin123
```

> Gera uma SECRET_KEY segura: `python -c "import secrets; print(secrets.token_hex(32))"`
> **Nunca versionar o .env.**

## Arrancar

```bash
python app.py
# → http://127.0.0.1:5000
```

---

## SQL — ordem de execução (phpMyAdmin → separador SQL)

```
1. seed.py (python seed.py)          ← estrutura base + ciclos (se 1.ª vez)
2. sql/seed_auth_final.sql           ← roles + utilizadores demo
3. sql/seed_estrutura_extra.sql      ← CTEs, EFA, FMC, Erasmus+, Área Docente
4. sql/seed_full_moodle_demo.sql     ← matrículas, classificações, tarefas,
                                        entregas, eventos, notificações
```

`sql/diagnostico_duplicados.sql` → apenas SELECT, para verificar integridade.

---

## Utilizadores demo (⚠️ apenas local)

| Utilizador | Password | Role | Acessos |
|---|---|---|---|
| `admin` | `admin123` | admin | Tudo + painel /admin |
| `docente` | `docente123` | docente | Área docente, manual do formador |
| `aluno` | `aluno123` | aluno | Campus, classificações, tarefas, calendário |
| — | — | visitante | Apenas áreas públicas |

Login legacy do painel: `/admin/login` com `ADMIN_PASSWORD` (continua a funcionar).

---

## Estrutura do campus

1. **Área Institucional** — Regulamento, Projeto Educativo, Plano de Atividades, EQAVET, Erasmus+, Manuais, Biblioteca, Centro Qualifica
2. **Ciclos Formativos Profissionais** — 10.º/11.º/12.º ano, disciplinas, FCT, PAP
3. **Centros Tecnológicos** — CTE Informática (Programação, IA, Robótica, RV) e CTE Industrial (CNC, CAD/CAM, Automatização, Indústria 5.0, Segurança)
4. **EFA** — Escolar, Profissional + 4 cursos EFA
5. **Formação Modular Certificada**
6. **Erasmus+** — mobilidades, relatórios, difusão
7. **Área Docente** *(restrita: admin/docente)* — planificações, instrumentos, atas, rúbricas, EQAVET, seguimento

## Estrutura de cada disciplina

Informação Geral · Conteúdos · Avaliação · Evidências · Comunicação

---

## Funcionalidades reais

- ✅ Login/logout por roles com hash de password
- ✅ Proteção de rotas (`login_required`, `role_required`) + fallback ADMIN_PASSWORD
- ✅ Painel admin: áreas, documentos, ciclos, disciplinas, secções, recursos (CRUD + upload + flash)
- ✅ Upload e eliminação física de ficheiros
- ✅ **Matrículas** (aluno ↔ ciclo) com progresso e estado
- ✅ **Classificações** (`/as-minhas-classificacoes`)
- ✅ **Tarefas e entregas** (`/as-minhas-tarefas`)
- ✅ **Calendário do campus** (`/calendario`) — avaliações, entregas, FCT, PAP
- ✅ **Notificações** reais (BD) no sino da topbar, com badge
- ✅ Dashboards distintos por role (visitante/aluno/docente/admin)
- ✅ Fallback seguro: se uma tabela faltar ou a BD cair, a página renderiza com aviso na consola (nunca 500)
- ✅ Etiquetas de ficheiro: Abrir PDF / Abrir documento / Ver imagem / Abrir ligação / Sem ficheiro

## Preparado para futura integração

- Mensageria interna (modal informativo)
- Gestão de utilizadores/roles no painel admin
- Edição de perfil e alteração de palavra-passe
- Importação em massa de recursos
- Turmas atribuídas ao docente

---

## Rotas principais

| Rota | Acesso |
|---|---|
| `/` | Público (dashboard por role) |
| `/login` · `/logout` | Público / autenticado |
| `/portal` · `/portal/<slug>` | Público (área-docente e manual-formador: admin/docente) |
| `/ciclos` · `/ciclos/<id>` · `/disciplinas/<id>` | Público |
| `/as-minhas-classificacoes` | Autenticado |
| `/as-minhas-tarefas` | Autenticado |
| `/calendario` | Autenticado |
| `/admin` (+ tabs) | Admin |
| `/admin/login` | Legacy ADMIN_PASSWORD |

---

## Testes rápidos

```bash
python -m py_compile app.py decorators.py services/moodle_service.py \
  routes/dashboard_routes.py routes/auth_routes.py routes/admin_routes.py
python app.py
```

Checklist manual: login com os 3 utilizadores demo, verificar dashboards, bloqueios de rol (aluno → /admin deve redirecionar), classificações/tarefas/calendário do aluno, sino de notificações, logout.

## Não versionar

```gitignore
.env
static/uploads/
venv/
__pycache__/
*.pyc
```

## Limitações conhecidas

- Entregas de ficheiros pelo aluno ainda não têm formulário de upload (estrutura de BD pronta)
- Notificações não têm "marcar como lida" na UI (campo `lida` já existe)
- Vista docente de correção de entregas é demo

---

*Academia Profissional Prof. Albino de Matos — Escola Profissional Vértice*

/**
 * Academia Vertice — Campus Virtual
 * main.js — Interacciones del lado cliente.
 *
 * Solo se ocupa de:
 *  - Modal (abrir / cerrar)
 *  - Toasts
 *  - Menú responsive
 *  - Tabs de detalle de curso
 *  - Acciones simuladas (perfil, soporte)
 *
 * NO renderiza vistas. NO depende de DATA. El HTML viene del servidor.
 */

// ──────────────────────────────────────────────
// MODAL
// ──────────────────────────────────────────────

function abrirModal(titulo, htmlContenido, footerHtml = '') {
  const overlay = document.getElementById('modal-overlay');
  if (!overlay) return;
  overlay.querySelector('.modal-head h3').textContent = titulo;
  overlay.querySelector('.modal-body').innerHTML = htmlContenido;
  overlay.querySelector('.modal-footer').innerHTML =
    footerHtml + `<button class="btn btn-secondary" onclick="cerrarModal()">Fechar</button>`;
  overlay.classList.add('open');
}

function cerrarModal() {
  const overlay = document.getElementById('modal-overlay');
  if (overlay) overlay.classList.remove('open');
}

// Cerrar modal al hacer clic en el fondo
document.addEventListener('DOMContentLoaded', () => {
  const overlay = document.getElementById('modal-overlay');
  if (overlay) {
    overlay.addEventListener('click', function (e) {
      if (e.target === this) cerrarModal();
    });
  }
});

// ──────────────────────────────────────────────
// TOAST
// ──────────────────────────────────────────────

function mostrarToast(mensaje, tipo = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = `toast ${tipo}`;
  const iconos = { success: '✓', warning: '⚠', info: 'ℹ', danger: '✕' };
  toast.innerHTML = `<span>${iconos[tipo] || 'ℹ'}</span> ${mensaje}`;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3600);
}

// ──────────────────────────────────────────────
// MENÚ RESPONSIVE
// ──────────────────────────────────────────────

function toggleSidebar() {
  const sidebar = document.querySelector('.sidebar');
  const toggle = document.getElementById('menu-toggle');
  if (!sidebar) return;

  const isOpen = sidebar.classList.toggle('open');
  if (toggle) toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
}

function closeSidebar() {
  const sidebar = document.querySelector('.sidebar');
  const toggle = document.getElementById('menu-toggle');
  if (!sidebar) return;

  sidebar.classList.remove('open');
  if (toggle) toggle.setAttribute('aria-expanded', 'false');
}

document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.getElementById('menu-toggle');
  const sidebar = document.querySelector('.sidebar');

  function checkMobile() {
    const isMobile = window.innerWidth <= 860;
    if (toggle) {
      toggle.style.display = isMobile ? 'flex' : 'none';
      toggle.setAttribute('aria-expanded', sidebar?.classList.contains('open') ? 'true' : 'false');
    }

    // Al volver a escritorio, el menú no debe quedar arrastrando el estado móvil.
    if (!isMobile) closeSidebar();
  }

  checkMobile();
  window.addEventListener('resize', checkMobile);

  if (toggle) {
    toggle.addEventListener('click', (event) => {
      event.stopPropagation();
      toggleSidebar();
    });
  }

  // Cerrar el menú móvil al pulsar fuera o al entrar en una opción.
  document.addEventListener('click', (event) => {
    if (window.innerWidth > 860 || !sidebar?.classList.contains('open')) return;
    if (sidebar.contains(event.target) || toggle?.contains(event.target)) return;
    closeSidebar();
  });

  if (sidebar) {
    sidebar.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', () => {
        if (window.innerWidth <= 860) closeSidebar();
      });
    });
  }

  // Botón flotante de ayuda
  const helpBtn = document.getElementById('floating-help');
  if (helpBtn) helpBtn.addEventListener('click', abrirModalSoporte);
});

// ──────────────────────────────────────────────
// SUPORTE E PERFIL
// ──────────────────────────────────────────────

function abrirModalSoporte() {
  abrirModal('Suporte técnico', `
    <p style="font-size:13px;color:var(--muted);margin-bottom:14px">
      Tens algum problema técnico? Contacta a equipa de suporte do campus.
    </p>
    <div style="display:flex;flex-direction:column;gap:8px">
      <div style="display:flex;gap:8px;align-items:center;font-size:13px">
        📧 <a href="mailto:geral@academiaprofissional.pt">geral@academiaprofissional.pt</a>
      </div>
      <div style="display:flex;gap:8px;align-items:center;font-size:13px">
        🕐 <span>Seg–Sex, 9:00–18:00</span>
      </div>
      <div style="display:flex;gap:8px;align-items:center;font-size:13px">
        💬 <span>Chat em direto disponível em horário letivo</span>
      </div>
    </div>
  `);
}

function abrirNotificacoes() {
  const data = document.getElementById('notif-data');
  const html = data ? data.innerHTML
                    : '<p class="modal-text">Sem notificações novas.</p>';
  abrirModal('Notificações', `<div class="notif-list">${html}</div>`);
}

function abrirMensagens() {
  abrirModal('Mensagens', `
    <p class="modal-text" style="margin-bottom:8px">
      A mensageria interna ainda não está disponível nesta versão do campus.
    </p>
    <p class="modal-text" style="font-size:12px;color:var(--muted)">
      Entretanto, podes contactar a escola em
      <a href="mailto:geral@academiaprofissional.pt">geral@academiaprofissional.pt</a>.
    </p>`);
}

function _msgFutura() {
  mostrarToast('Esta funcionalidade ainda não está disponível.', 'info');
}

function abrirModalPerfil() {
  const avatarEl = document.querySelector('.avatar');
  const nameEl   = document.querySelector('.user-name');
  const roleEl   = nameEl ? nameEl.closest('div')?.querySelector('span:last-child') : null;

  const nombre    = nameEl   ? nameEl.textContent.trim()   : '';
  const iniciais  = avatarEl ? avatarEl.textContent.trim() : '?';
  const role      = roleEl   ? roleEl.textContent.trim()   : '';

  if (!nombre) {
    // Visitante — não devia chegar aqui, mas por segurança
    _msgFutura();
    return;
  }

  abrirModal('O meu perfil', `
    <div class="profile-card">
      <div class="profile-avatar">${iniciais}</div>
      <div class="profile-info">
        <div class="profile-name">${nombre}</div>
        <div class="profile-role">${role ? role + ' · ' : ''}Academia Profissional Prof. Albino de Matos</div>
      </div>
    </div>
    <div class="profile-actions">
      <button class="btn btn-secondary w-full"
              onclick="_msgFutura()">✏ Editar perfil</button>
      <button class="btn btn-secondary w-full"
              onclick="_msgFutura()">🔒 Alterar palavra-passe</button>
      <button class="btn btn-secondary w-full"
              onclick="cerrarModal(); abrirNotificacoes()">🔔 Notificações</button>
      <button class="btn btn-danger w-full"
              onclick="cerrarSesion()">→ Terminar sessão</button>
    </div>
  `);
}

function cerrarSesion() {
  const form = document.createElement('form');
  form.method = 'POST';
  form.action = '/logout';
  document.body.appendChild(form);
  form.submit();
}

// ──────────────────────────────────────────────
// TABS EN DETALLE DE CURSO
// ──────────────────────────────────────────────

function cambiarTabCurso(nombreTab, btnEl) {
  // Ocultar todos los paneles
  document.querySelectorAll('.tab-panel').forEach(p => p.style.display = 'none');

  // Desactivar todos los botones de tab
  document.querySelectorAll('#curso-tabs .tab').forEach(b => b.classList.remove('active'));

  // Mostrar el panel seleccionado
  const panel = document.getElementById('tab-' + nombreTab);
  if (panel) panel.style.display = '';

  // Activar el botón pulsado
  if (btnEl) btnEl.classList.add('active');
}
// ──────────────────────────────────────────────
// CALENDÁRIO VISUAL MENSAL
// ──────────────────────────────────────────────

(function () {
  const monthNames = [
    'janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
    'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'
  ];

  function parseISODate(value) {
    if (!value) return null;
    const parts = String(value).slice(0, 10).split('-').map(Number);
    if (parts.length !== 3 || parts.some(Number.isNaN)) return null;
    return new Date(parts[0], parts[1] - 1, parts[2]);
  }

  function isoDate(date) {
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
  }

  function sameDay(a, b) {
    return a && b && isoDate(a) === isoDate(b);
  }

  function eventTypeLabel(type) {
    const labels = {
      avaliacao: 'Avaliação',
      entrega: 'Entrega',
      fct: 'FCT',
      pap: 'PAP',
      evento: 'Evento da escola',
      tarefa: 'Tarefa'
    };
    return labels[type] || 'Evento';
  }

  function eventTypeIcon(type) {
    const icons = {
      avaliacao: '📝',
      entrega: '📤',
      fct: '🏢',
      pap: '🎓',
      evento: '📅',
      tarefa: '📌'
    };
    return icons[type] || '📅';
  }

  function openCalendarEventModal(event) {
    const title = event.title || 'Evento';
    const label = event.typeLabel || eventTypeLabel(event.type);
    const icon = event.icon || eventTypeIcon(event.type);
    const date = parseISODate(event.date);
    const dateText = date
      ? `${date.getDate()} de ${monthNames[date.getMonth()]} de ${date.getFullYear()}`
      : event.date || '';

    const html = `
      <div class="calendar-modal-detail">
        <div class="calendar-modal-badge cal-type-${event.type || 'evento'}">${icon} ${label}</div>
        <p><strong>Data:</strong> ${dateText}</p>
        ${event.time ? `<p><strong>Hora:</strong> ${event.time}</p>` : ''}
        ${event.disciplina ? `<p><strong>Disciplina:</strong> ${event.disciplina}</p>` : ''}
        ${event.estado ? `<p><strong>Estado:</strong> ${event.estado}</p>` : ''}
        ${event.description ? `<p class="calendar-modal-description">${event.description}</p>` : ''}
        ${event.url ? `<a class="btn btn-primary btn-sm" href="${event.url}">Ver tarefa</a>` : ''}
      </div>
    `;

    if (typeof abrirModal === 'function') {
      abrirModal(title, html);
    } else {
      alert(`${title}\n${dateText}`);
    }
  }

  function openDayEventsModal(dateKey, events) {
    const date = parseISODate(dateKey);
    const title = date
      ? `Eventos de ${date.getDate()} de ${monthNames[date.getMonth()]}`
      : 'Eventos do dia';

    const html = events.map(ev => `
      <button type="button" class="calendar-day-modal-item" data-event-id="${ev._id}">
        <span class="calendar-event-dot cal-type-${ev.type || 'evento'}"></span>
        <span>
          <strong>${ev.title || 'Evento'}</strong>
          <small>${ev.time ? ev.time + ' · ' : ''}${ev.typeLabel || eventTypeLabel(ev.type)}</small>
        </span>
      </button>
    `).join('');

    abrirModal(title, `<div class="calendar-day-modal-list">${html}</div>`);

    setTimeout(() => {
      document.querySelectorAll('.calendar-day-modal-item[data-event-id]').forEach(btn => {
        btn.addEventListener('click', () => {
          const ev = events.find(item => String(item._id) === btn.dataset.eventId);
          if (ev) openCalendarEventModal(ev);
        });
      });
    }, 0);
  }

  function initVisualCalendar() {
    const root = document.getElementById('visual-calendar');
    if (!root) return;

    const grid = root.querySelector('[data-cal-grid]');
    const currentLabel = root.querySelector('[data-cal-current]');
    const prevBtn = root.querySelector('[data-cal-prev]');
    const nextBtn = root.querySelector('[data-cal-next]');
    const todayBtn = root.querySelector('[data-cal-today]');

    const rawEvents = Array.isArray(window.calendarEvents) ? window.calendarEvents : [];
    const events = rawEvents
      .filter(ev => ev && ev.date)
      .map((ev, index) => ({
        ...ev,
        _id: String(index),
        type: ev.type || 'evento',
        typeLabel: ev.typeLabel || eventTypeLabel(ev.type),
        icon: ev.icon || eventTypeIcon(ev.type),
      }));

    const today = new Date();
    const currentMonthHasEvents = events.some(ev => {
      const d = parseISODate(ev.date);
      return d && d.getFullYear() === today.getFullYear() && d.getMonth() === today.getMonth();
    });
    const firstEventDate = events.length ? parseISODate(events[0].date) : null;
    let visibleMonth = currentMonthHasEvents || !firstEventDate
      ? new Date(today.getFullYear(), today.getMonth(), 1)
      : new Date(firstEventDate.getFullYear(), firstEventDate.getMonth(), 1);

    function render() {
      grid.innerHTML = '';
      const year = visibleMonth.getFullYear();
      const month = visibleMonth.getMonth();
      currentLabel.textContent = `${monthNames[month]} ${year}`;

      const firstDay = new Date(year, month, 1);
      const startOffset = (firstDay.getDay() + 6) % 7; // segunda-feira = 0
      const startDate = new Date(year, month, 1 - startOffset);

      for (let i = 0; i < 42; i++) {
        const day = new Date(startDate);
        day.setDate(startDate.getDate() + i);
        const key = isoDate(day);
        const dayEvents = events.filter(ev => ev.date === key);
        const visibleEvents = dayEvents.slice(0, 3);
        const hiddenCount = Math.max(dayEvents.length - visibleEvents.length, 0);

        const cell = document.createElement('div');
        cell.className = 'app-calendar-day';
        if (day.getMonth() !== month) cell.classList.add('is-muted');
        if (sameDay(day, today)) cell.classList.add('is-today');
        if (dayEvents.length) cell.classList.add('has-events');

        const number = document.createElement('div');
        number.className = 'app-calendar-day-number';
        number.textContent = day.getDate();
        cell.appendChild(number);

        const list = document.createElement('div');
        list.className = 'app-calendar-events';

        visibleEvents.forEach(ev => {
          const item = document.createElement('button');
          item.type = 'button';
          item.className = `app-calendar-event cal-type-${ev.type}`;
          item.title = ev.title;
          item.innerHTML = `<span class="calendar-event-dot cal-type-${ev.type}"></span><span>${ev.time ? ev.time + ' · ' : ''}${ev.title}</span>`;
          item.addEventListener('click', (event) => {
            event.stopPropagation();
            openCalendarEventModal(ev);
          });
          list.appendChild(item);
        });

        if (hiddenCount) {
          const more = document.createElement('button');
          more.type = 'button';
          more.className = 'app-calendar-more';
          more.textContent = `+${hiddenCount} eventos`;
          more.addEventListener('click', (event) => {
            event.stopPropagation();
            openDayEventsModal(key, dayEvents);
          });
          list.appendChild(more);
        }

        cell.appendChild(list);
        if (dayEvents.length) {
          cell.addEventListener('click', () => openDayEventsModal(key, dayEvents));
        }
        grid.appendChild(cell);
      }
    }

    prevBtn?.addEventListener('click', () => {
      visibleMonth = new Date(visibleMonth.getFullYear(), visibleMonth.getMonth() - 1, 1);
      render();
    });

    nextBtn?.addEventListener('click', () => {
      visibleMonth = new Date(visibleMonth.getFullYear(), visibleMonth.getMonth() + 1, 1);
      render();
    });

    todayBtn?.addEventListener('click', () => {
      visibleMonth = new Date(today.getFullYear(), today.getMonth(), 1);
      render();
    });

    render();
  }

  document.addEventListener('DOMContentLoaded', initVisualCalendar);
})();

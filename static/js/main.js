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
  if (sidebar) sidebar.classList.toggle('open');
}

document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.getElementById('menu-toggle');

  function checkMobile() {
    if (toggle) toggle.style.display = window.innerWidth <= 860 ? 'flex' : 'none';
  }
  checkMobile();
  window.addEventListener('resize', checkMobile);

  if (toggle) toggle.addEventListener('click', toggleSidebar);

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

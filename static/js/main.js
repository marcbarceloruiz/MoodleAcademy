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
    footerHtml + `<button class="btn btn-secondary" onclick="cerrarModal()">Cerrar</button>`;
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
  const iconos = { success: '✓', warning: '⚠', info: 'ℹ' };
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
// SOPORTE Y PERFIL (modales simulados)
// ──────────────────────────────────────────────

function abrirModalSoporte() {
  abrirModal('Soporte técnico', `
    <p style="font-size:13px;color:var(--muted);margin-bottom:14px">
      ¿Tienes algún problema técnico? Contacta con nuestro equipo de soporte.
    </p>
    <div style="display:flex;flex-direction:column;gap:8px">
      <div style="display:flex;gap:8px;align-items:center;font-size:13px">
        📧 <a href="mailto:soporte@academiavertice.es">soporte@academiavertice.es</a>
      </div>
      <div style="display:flex;gap:8px;align-items:center;font-size:13px">
        📞 <span>900 123 456 (L-V, 9:00-18:00)</span>
      </div>
      <div style="display:flex;gap:8px;align-items:center;font-size:13px">
        💬 <span>Chat en vivo disponible en horario lectivo</span>
      </div>
    </div>
  `);
}

function abrirModalPerfil() {
  // Los datos del usuario llegan por atributos data- del DOM para no depender de JS global
  const avatarEl = document.querySelector('.avatar');
  const nameEl   = document.querySelector('.user-name');
  const nombre   = nameEl ? nameEl.textContent.trim() : 'Usuario';
  const iniciales = avatarEl ? avatarEl.textContent.trim() : '??';

  abrirModal('Mi perfil', `
    <div class="profile-card">
      <div class="profile-avatar">${iniciales}</div>
      <div class="profile-info">
        <div class="profile-name">${nombre}</div>
        <div class="profile-role">Professora · Academia Vertice</div>
      </div>
    </div>
    <div class="profile-actions">
      <button class="btn btn-secondary w-full"
              onclick="mostrarToast('Función: editar perfil', 'info')">✏ Editar perfil</button>
      <button class="btn btn-secondary w-full"
              onclick="mostrarToast('Función: cambiar contraseña', 'info')">🔒 Cambiar contraseña</button>
      <button class="btn btn-secondary w-full"
              onclick="mostrarToast('Función: notificaciones', 'info')">🔔 Notificaciones</button>
      <button class="btn btn-danger w-full"
        onclick="cerrarSesion()">→ Cerrar sesión</button>
    </div>
  `);
}

function cerrarSesion() {
  if (window.location.pathname.startsWith('/admin')) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/admin/logout';
    document.body.appendChild(form);
    form.submit();
    return;
  }

  mostrarToast('Sesión cerrada', 'warning');
  cerrarModal();
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

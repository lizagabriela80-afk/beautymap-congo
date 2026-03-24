/* ============================================================
   BEAUTYMAP CONGO — main.js
   ============================================================ */

'use strict';

/* ==================== NAV ==================== */
window.addEventListener('scroll', () => {
  document.getElementById('nav')?.classList.toggle('scrolled', window.scrollY > 40);
});

function toggleUserMenu() {
  document.getElementById('nav-dropdown')?.classList.toggle('open');
}
document.addEventListener('click', e => {
  const menu = document.getElementById('nav-user-menu');
  if (menu && !menu.contains(e.target)) {
    document.getElementById('nav-dropdown')?.classList.remove('open');
  }
});

function toggleMobileNav() {
  document.getElementById('nav-links')?.classList.toggle('mobile-open');
}

/* ==================== TOAST ==================== */
function toast(msg, type = 'default', duration = 3500) {
  const c = document.getElementById('toasts');
  if (!c) return;
  const t = document.createElement('div');
  t.className = 'toast';
  const colors = { success: '#5EC98A', error: '#E07060', warning: 'var(--gold-lt)', default: 'var(--txt)' };
  t.innerHTML = `<span class="toast-msg" style="color:${colors[type] || colors.default}">${msg}</span>
    <button onclick="this.parentElement.remove()" style="background:none;border:none;color:var(--mut);font-size:1rem;cursor:pointer;padding:0;line-height:1;margin-left:auto">✕</button>`;
  c.appendChild(t);
  setTimeout(() => t.remove(), duration + 400);
}

/* ==================== MODALS ==================== */
function openOv(id) {
  const el = document.getElementById(id);
  if (el) { el.classList.add('open'); document.body.style.overflow = 'hidden'; }
}
function closeOv(id) {
  const el = document.getElementById(id);
  if (el) { el.classList.remove('open'); document.body.style.overflow = ''; }
}
document.addEventListener('click', e => {
  if (e.target.classList.contains('ov')) {
    e.target.classList.remove('open');
    document.body.style.overflow = '';
  }
});
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.ov.open').forEach(el => { el.classList.remove('open'); document.body.style.overflow = ''; });
  }
});

/* ==================== TABS ==================== */
function switchTab(btn, targetId, groupPrefix) {
  const container = btn.closest('.tabs').parentElement;
  container.querySelectorAll('.tab').forEach(t => t.classList.remove('on'));
  btn.classList.add('on');
  if (groupPrefix) {
    container.querySelectorAll(`[id^="${groupPrefix}"]`).forEach(el => el.style.display = 'none');
  }
  const target = document.getElementById(targetId);
  if (target) target.style.display = 'block';
}

/* ==================== COPY TO CLIPBOARD ==================== */
function copyToClipboard(text, label = 'Copié !') {
  navigator.clipboard.writeText(text).then(() => toast(`📋 ${label}`, 'success')).catch(() => {
    const ta = document.createElement('textarea');
    ta.value = text; document.body.appendChild(ta); ta.select();
    document.execCommand('copy'); document.body.removeChild(ta);
    toast(`📋 ${label}`, 'success');
  });
}
function copyPromo(el) {
  const code = el.textContent.trim();
  copyToClipboard(code, `Code ${code} copié !`);
}

/* ==================== STAR RATING ==================== */
function initStarRating(containerId, inputId) {
  const container = document.getElementById(containerId);
  const input = document.getElementById(inputId);
  if (!container || !input) return;
  const stars = container.querySelectorAll('span');
  stars.forEach((star, i) => {
    star.addEventListener('click', () => {
      input.value = i + 1;
      stars.forEach((s, j) => { s.textContent = j <= i ? '★' : '☆'; s.style.color = j <= i ? 'var(--gold)' : 'var(--mut)'; });
    });
    star.addEventListener('mouseenter', () => {
      stars.forEach((s, j) => { s.style.color = j <= i ? 'var(--gold-lt)' : 'var(--mut)'; });
    });
    star.addEventListener('mouseleave', () => {
      const current = parseInt(input.value) || 0;
      stars.forEach((s, j) => { s.style.color = j < current ? 'var(--gold)' : 'var(--mut)'; });
    });
  });
}

/* ==================== SLOT PICKER ==================== */
function pickSlot(el) {
  document.querySelectorAll('.slot:not(.taken)').forEach(s => s.classList.remove('picked'));
  el.classList.add('picked');
  const input = document.getElementById('selected-time');
  if (input) input.value = el.dataset.time || el.textContent.trim();
}

/* ==================== AVAILABLE SLOTS (AJAX) ==================== */
async function loadSlots(shopId, serviceId, date) {
  const container = document.getElementById('slots-container');
  const input = document.getElementById('selected-time');
  if (!container) return;

  container.innerHTML = '<div style="color:var(--mut);font-size:.84rem;padding:10px">Chargement des créneaux…</div>';

  try {
    const res = await fetch(`/bookings/creneaux/?shop=${shopId}&service=${serviceId}&date=${date}`);
    const data = await res.json();
    if (!data.slots || data.slots.length === 0) {
      container.innerHTML = '<div style="color:var(--mut);font-size:.84rem;padding:10px">Aucun créneau disponible ce jour.</div>';
      return;
    }
    container.innerHTML = data.slots.map(s => `
      <div class="slot ${s.available ? '' : 'taken'}" onclick="${s.available ? 'pickSlot(this)' : ''}" data-time="${s.time}">
        ${s.time}
      </div>`).join('');
    if (input) input.value = '';
  } catch (e) {
    container.innerHTML = '<div style="color:var(--red);font-size:.84rem;padding:10px">Erreur lors du chargement.</div>';
  }
}

/* ==================== FAVORITE TOGGLE (AJAX) ==================== */
async function toggleFavAjax(btn, shopId) {
  btn.disabled = true;
  try {
    const res = await fetch(`/boutique/${shopId}/favori/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': getCsrfToken(), 'Content-Type': 'application/json' },
    });
    const data = await res.json();
    if (data.is_favorite) {
      btn.innerHTML = '❤️'; btn.classList.add('on');
      toast('❤️ Ajouté aux favoris !', 'success');
    } else {
      btn.innerHTML = '🤍'; btn.classList.remove('on');
      toast('💔 Retiré des favoris');
    }
  } catch (e) {
    toast('Erreur réseau', 'error');
  } finally {
    btn.disabled = false;
  }
}

/* ==================== CANCEL/CONFIRM BOOKING (AJAX) ==================== */
async function cancelBooking(pk, btn) {
  if (!confirm('Annuler ce rendez-vous ?')) return;
  btn.disabled = true;
  try {
    const res = await fetch(`/bookings/${pk}/annuler/`, {
      method: 'POST', headers: { 'X-CSRFToken': getCsrfToken() }
    });
    const data = await res.json();
    if (data.success) {
      btn.closest('tr')?.querySelector('.st')?.outerHTML;
      const st = btn.closest('tr')?.querySelector('.st');
      if (st) { st.className = 'st st-no'; st.textContent = '✗ Annulé'; }
      btn.remove();
      toast('✅ Rendez-vous annulé', 'success');
    } else {
      toast(data.error || 'Erreur', 'error');
    }
  } catch (e) { toast('Erreur réseau', 'error'); }
  finally { btn.disabled = false; }
}

async function confirmBooking(pk, btn) {
  btn.disabled = true;
  try {
    const res = await fetch(`/bookings/${pk}/confirmer/`, {
      method: 'POST', headers: { 'X-CSRFToken': getCsrfToken() }
    });
    const data = await res.json();
    if (data.success) {
      const st = btn.closest('tr')?.querySelector('.st');
      if (st) { st.className = 'st st-ok'; st.textContent = '✓ Confirmé'; }
      btn.remove();
      toast('✅ Rendez-vous confirmé !', 'success');
    }
  } catch (e) { toast('Erreur réseau', 'error'); }
  finally { btn.disabled = false; }
}

/* ==================== REVIEW SUBMIT (AJAX) ==================== */
async function submitReview(shopSlug) {
  const rating = document.getElementById('review-rating')?.value;
  const comment = document.getElementById('review-comment')?.value?.trim();
  const title = document.getElementById('review-title')?.value?.trim();

  if (!rating || rating === '0') { toast('⚠️ Veuillez choisir une note', 'warning'); return; }
  if (!comment) { toast('⚠️ Le commentaire est requis', 'warning'); return; }

  const btn = document.getElementById('submit-review-btn');
  if (btn) { btn.disabled = true; btn.textContent = 'Publication…'; }

  try {
    const res = await fetch(`/reviews/boutique/${shopSlug}/avis/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': getCsrfToken(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ rating, comment, title })
    });
    const data = await res.json();
    if (data.success) {
      closeOv('ov-review');
      toast('⭐ ' + data.message, 'success');
    } else { toast(data.error || 'Erreur', 'error'); }
  } catch (e) { toast('Erreur réseau', 'error'); }
  finally { if (btn) { btn.disabled = false; btn.textContent = 'Publier l\'avis'; } }
}

/* ==================== SEND MESSAGE (AJAX) ==================== */
async function sendMessage(convId) {
  const inp = document.getElementById('chat-input');
  if (!inp || !inp.value.trim()) return;
  const content = inp.value.trim();
  inp.value = '';

  appendMessage(content, true);

  try {
    await fetch(`/messages/${convId}/envoyer/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': getCsrfToken(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ content })
    });
  } catch (e) { toast('Message non envoyé', 'error'); }
}

function appendMessage(content, isMine, senderInitials = '', time = '') {
  const box = document.getElementById('chat-box');
  if (!box) return;
  const now = time || new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
  const div = document.createElement('div');
  div.className = `cm ${isMine ? 'me' : 'them'}`;
  div.innerHTML = `${escapeHtml(content)}<div class="cm-time">${now}</div>`;
  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
}

/* ==================== OTP ==================== */
async function sendOtp() {
  const phone = document.getElementById('otp-phone')?.value?.trim();
  if (!phone) { toast('Numéro requis', 'warning'); return; }
  const btn = document.getElementById('send-otp-btn');
  if (btn) { btn.disabled = true; btn.textContent = 'Envoi…'; }
  try {
    const res = await fetch('/auth/otp/send/', {
      method: 'POST',
      headers: { 'X-CSRFToken': getCsrfToken(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone })
    });
    const data = await res.json();
    if (data.success) {
      toast('📲 Code envoyé !', 'success');
      document.getElementById('otp-code-section')?.classList.remove('hidden');
      startOtpTimer(btn);
    }
  } catch (e) { toast('Erreur réseau', 'error'); }
  finally { if (btn) btn.textContent = 'Renvoyer le code'; }
}

function startOtpTimer(btn) {
  let seconds = 60;
  const iv = setInterval(() => {
    seconds--;
    if (btn) btn.textContent = `Renvoyer dans ${seconds}s`;
    if (seconds <= 0) {
      clearInterval(iv);
      if (btn) { btn.disabled = false; btn.textContent = 'Renvoyer le code'; }
    }
  }, 1000);
}

async function verifyOtp() {
  const phone = document.getElementById('otp-phone')?.value?.trim();
  const code  = document.getElementById('otp-code')?.value?.trim();
  if (!phone || !code) { toast('Renseignez le numéro et le code', 'warning'); return; }
  const btn = document.getElementById('verify-otp-btn');
  if (btn) { btn.disabled = true; btn.textContent = 'Vérification…'; }
  try {
    const res = await fetch('/auth/otp/verify/', {
      method: 'POST',
      headers: { 'X-CSRFToken': getCsrfToken(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone, code })
    });
    const data = await res.json();
    if (data.success) { window.location.href = data.redirect || '/dashboard/'; }
    else { toast(data.message || 'Code invalide', 'error'); }
  } catch (e) { toast('Erreur réseau', 'error'); }
  finally { if (btn) { btn.disabled = false; btn.textContent = 'Vérifier'; } }
}

/* ==================== MAP ==================== */
let mapInstance = null;
let mapMarkers = [];

function initMap(shopsData) {
  if (mapInstance || !document.getElementById('leaflet-map')) return;
  mapInstance = L.map('leaflet-map', { zoomControl: true }).setView([-4.2750, 15.2760], 13);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors', maxZoom: 19
  }).addTo(mapInstance);
  if (shopsData) renderMapMarkers(shopsData);
}

function renderMapMarkers(shops) {
  mapMarkers.forEach(m => m.remove());
  mapMarkers = [];
  shops.forEach(s => {
    if (!s.lat || !s.lng) return;
    const icon = L.divIcon({
      html: `<div style="width:42px;height:42px;border-radius:50%;background:var(--ink2,#111);border:2.5px solid #C9973A;display:flex;align-items:center;justify-content:center;font-size:1.15rem;box-shadow:0 4px 18px rgba(0,0,0,.8);cursor:pointer">${s.category_emoji || '🏪'}</div>`,
      className: '', iconSize: [42, 42], iconAnchor: [21, 21]
    });
    const m = L.marker([s.lat, s.lng], { icon }).addTo(mapInstance);
    m.bindPopup(`
      <div class="map-popup">
        <div class="mp-name">${s.name}</div>
        <div class="mp-meta">📍 ${s.quartier} · ${s.category_emoji || ''} ${s.category}</div>
        <div class="mp-meta">⭐ ${s.rating ? s.rating.toFixed(1) : 'Nouveau'} · ${s.is_open ? '<span style="color:#2E9458">Ouvert</span>' : '<span style="color:#C0412E">Fermé</span>'}</div>
        <a href="/boutique/${s.slug}/" class="mp-btn">Voir la boutique →</a>
      </div>`);
    mapMarkers.push(m);
  });
}

async function filterMap(cat, btn) {
  document.querySelectorAll('.map-pills .pill').forEach(p => p.classList.remove('on'));
  btn.classList.add('on');
  try {
    const res = await fetch(`/api/map-data/?category=${cat}`);
    const data = await res.json();
    renderMapMarkers(data.shops);
  } catch (e) { toast('Erreur chargement carte', 'error'); }
}

/* ==================== EXPLORE FILTERS ==================== */
function filterExplore(cat, btn) {
  document.querySelectorAll('.explore-pills .pill').forEach(p => p.classList.remove('on'));
  btn.classList.add('on');
  const url = new URL(window.location);
  if (cat) url.searchParams.set('category', cat);
  else url.searchParams.delete('category');
  url.searchParams.delete('page');
  window.location.href = url.toString();
}

/* ==================== COUNTER ANIMATION ==================== */
function animateCounters() {
  document.querySelectorAll('[data-count]').forEach(el => {
    const target = parseInt(el.dataset.count);
    const suffix = el.dataset.suffix || '';
    let current = 0;
    const step = Math.ceil(target / 60);
    const iv = setInterval(() => {
      current = Math.min(current + step, target);
      el.textContent = current.toLocaleString('fr-FR') + suffix;
      if (current >= target) clearInterval(iv);
    }, 22);
  });
}

/* ==================== DASHBOARD SIDEBAR ==================== */
function dashTab(tab, btn) {
  document.querySelectorAll('.sb-item').forEach(i => i.classList.remove('on'));
  if (btn) btn.classList.add('on');
  const url = new URL(window.location);
  url.searchParams.set('tab', tab);
  // Use history.pushState to avoid reload
  history.pushState({}, '', url.toString());
  loadDashTab(tab);
}

async function loadDashTab(tab) {
  const main = document.getElementById('dash-content');
  if (!main) return;
  main.innerHTML = '<div style="color:var(--mut);padding:40px;text-align:center">Chargement…</div>';
  try {
    const res = await fetch(`/dashboard/pro/?tab=${tab}`, {
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    });
    if (res.ok) main.innerHTML = await res.text();
  } catch (e) {
    main.innerHTML = '<div style="color:var(--red);padding:40px;text-align:center">Erreur de chargement.</div>';
  }
}

/* ==================== NOTIFICATIONS BADGE ==================== */
async function loadNotifCount() {
  try {
    const res = await fetch('/notifications/');
    const data = await res.json();
    const unread = data.notifications.filter(n => !n.is_read).length;
    document.querySelectorAll('.notif-count-badge').forEach(b => {
      b.textContent = unread;
      b.style.display = unread ? 'inline' : 'none';
    });
  } catch (e) {}
}

/* ==================== SEARCH ==================== */
function submitSearch(e) {
  if (e) e.preventDefault();
  const q = document.getElementById('search-input')?.value?.trim();
  if (q) window.location.href = `/explorer/?q=${encodeURIComponent(q)}`;
}

/* ==================== CSRF ==================== */
function getCsrfToken() {
  const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
  return cookie ? cookie.trim().split('=')[1] : (document.querySelector('[name=csrfmiddlewaretoken]')?.value || '');
}

/* ==================== UTILS ==================== */
function escapeHtml(str) {
  const d = document.createElement('div');
  d.appendChild(document.createTextNode(str));
  return d.innerHTML;
}

function debounce(fn, ms) {
  let t;
  return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
}

function formatPrice(n) {
  return new Intl.NumberFormat('fr-FR').format(n) + ' FCFA';
}

/* ==================== WEBSOCKET CHAT ==================== */
let ws = null;

function initWebSocket(convId) {
  if (!convId) return;
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
  ws = new WebSocket(`${protocol}://${window.location.host}/ws/chat/${convId}/`);

  ws.onopen = () => console.log('WS connected');
  ws.onclose = () => { setTimeout(() => initWebSocket(convId), 3000); };
  ws.onerror = e => console.error('WS error', e);

  ws.onmessage = e => {
    const data = JSON.parse(e.data);
    if (data.type === 'chat_message') {
      const msg = data.message;
      const isMine = msg.sender_id === parseInt(document.getElementById('current-user-id')?.value || 0);
      if (!isMine) appendMessage(msg.content, false, msg.sender_initials, msg.created_at);
    }
  };
}

function sendWsMessage(convId) {
  const inp = document.getElementById('chat-input');
  if (!inp || !inp.value.trim()) return;
  const content = inp.value.trim();

  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: 'message', content }));
    appendMessage(content, true, '', new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }));
    inp.value = '';
  } else {
    sendMessage(convId);
  }
}

/* ==================== INIT ==================== */
document.addEventListener('DOMContentLoaded', () => {
  // Animate counters on hero
  if (document.querySelector('[data-count]')) {
    animateCounters();
  }

  // Init star ratings
  if (document.getElementById('star-container')) {
    initStarRating('star-container', 'review-rating');
  }

  // Slot date change
  const dateInput = document.getElementById('booking-date');
  if (dateInput) {
    dateInput.addEventListener('change', () => {
      const shopId = document.getElementById('booking-shop-id')?.value;
      const serviceId = document.getElementById('booking-service')?.value;
      if (shopId && serviceId) loadSlots(shopId, serviceId, dateInput.value);
    });
    // Also on service change
    document.getElementById('booking-service')?.addEventListener('change', () => {
      if (dateInput.value) {
        const shopId = document.getElementById('booking-shop-id')?.value;
        loadSlots(shopId, document.getElementById('booking-service').value, dateInput.value);
      }
    });
  }

  // Live search debounce
  const searchInp = document.getElementById('search-input');
  if (searchInp) {
    searchInp.addEventListener('keypress', e => { if (e.key === 'Enter') submitSearch(e); });
  }

  // Chat enter key
  document.getElementById('chat-input')?.addEventListener('keypress', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      const convId = document.getElementById('conv-id')?.value;
      convId ? sendWsMessage(convId) : null;
    }
  });

  // Scroll chat to bottom
  const chatBox = document.getElementById('chat-box');
  if (chatBox) chatBox.scrollTop = chatBox.scrollHeight;

  // Init map if on map page
  const mapEl = document.getElementById('leaflet-map');
  if (mapEl) {
    const shopsDataEl = document.getElementById('shops-json-data');
    const shopsData = shopsDataEl ? JSON.parse(shopsDataEl.textContent) : [];
    // Need to load leaflet
    if (window.L) {
      initMap(shopsData);
    } else {
      const script = document.createElement('script');
      script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
      script.onload = () => initMap(shopsData);
      document.head.appendChild(script);
    }
  }

  // WS chat init
  const convIdEl = document.getElementById('conv-id');
  if (convIdEl) initWebSocket(convIdEl.value);

  // Load notif count
  if (document.body.dataset.authenticated === 'true') {
    loadNotifCount();
    setInterval(loadNotifCount, 60000);
  }
});

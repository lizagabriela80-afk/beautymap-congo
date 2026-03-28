/* ============================================================
   BEAUTYMAP CONGO — main.js  v2
   Améliorations : live-search, apiFetch centralisé,
   pull-to-refresh mobile, WS reconnexion exponentielle,
   accessibilité ARIA, appendMessage helper.
   ============================================================ */
'use strict';

/* ── CSRF ─────────────────────────────────────────────────── */
function getCsrfToken() {
  const c = document.cookie.split(';').find(x => x.trim().startsWith('csrftoken='));
  return c ? c.trim().split('=')[1] : (document.querySelector('[name=csrfmiddlewaretoken]')?.value || '');
}

/* ── Fetch helper avec gestion session expirée ───────────── */
async function apiFetch(url, opts = {}) {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken(), ...opts.headers },
    ...opts,
  });
  if (res.status === 401) {
    toast('Session expirée. Reconnectez-vous.', 'warning');
    setTimeout(() => { window.location.href = '/auth/login/?next=' + encodeURIComponent(window.location.pathname); }, 1500);
    throw new Error('Unauthorized');
  }
  return res;
}

/* ── NAV ─────────────────────────────────────────────────── */
window.addEventListener('scroll', () => {
  document.getElementById('nav')?.classList.toggle('scrolled', window.scrollY > 40);
}, { passive: true });

function toggleUserMenu() {
  const dd = document.getElementById('nav-dropdown');
  if (!dd) return;
  dd.classList.toggle('open');
  dd.setAttribute('aria-expanded', dd.classList.contains('open'));
}
document.addEventListener('click', e => {
  if (!document.getElementById('nav-user-menu')?.contains(e.target)) {
    document.getElementById('nav-dropdown')?.classList.remove('open');
  }
});

function toggleMobileNav() {
  const links = document.getElementById('nav-links');
  if (!links) return;
  const open = links.classList.toggle('mobile-open');
  links.setAttribute('aria-hidden', !open);
}

/* ── TOAST ───────────────────────────────────────────────── */
const TOAST_COLORS = { success:'#5EC98A', error:'#E07060', warning:'var(--gold-lt)', info:'var(--blue)', default:'var(--txt)' };

function toast(msg, type = 'default', duration = 3500) {
  const c = document.getElementById('toasts');
  if (!c) return;
  const t = document.createElement('div');
  t.className = 'toast';
  t.setAttribute('role', 'alert');
  t.innerHTML = `<span class="toast-msg" style="color:${TOAST_COLORS[type]||TOAST_COLORS.default}">${escapeHtml(msg)}</span>
    <button onclick="this.parentElement.remove()" style="background:none;border:none;color:var(--mut);cursor:pointer;margin-left:auto;font-size:1rem" aria-label="Fermer">✕</button>`;
  c.appendChild(t);
  setTimeout(() => t.remove(), duration + 400);
}

/* ── MODALS ──────────────────────────────────────────────── */
const _ovStack = [];
function openOv(id) {
  const el = document.getElementById(id); if (!el) return;
  el.classList.add('open'); el.setAttribute('aria-hidden','false');
  document.body.style.overflow = 'hidden'; _ovStack.push(id);
}
function closeOv(id) {
  const el = document.getElementById(id); if (!el) return;
  el.classList.remove('open'); el.setAttribute('aria-hidden','true');
  const i = _ovStack.indexOf(id); if (i !== -1) _ovStack.splice(i,1);
  if (!_ovStack.length) document.body.style.overflow = '';
}
document.addEventListener('click', e => { if (e.target.classList.contains('ov')) closeOv(e.target.id); });
document.addEventListener('keydown', e => { if (e.key==='Escape' && _ovStack.length) closeOv(_ovStack[_ovStack.length-1]); });

/* ── TABS ────────────────────────────────────────────────── */
function switchTab(btn, targetId, groupPrefix) {
  const container = btn.closest('.tabs')?.parentElement; if (!container) return;
  container.querySelectorAll('.tab').forEach(t => { t.classList.remove('on'); t.setAttribute('aria-selected','false'); });
  btn.classList.add('on'); btn.setAttribute('aria-selected','true');
  if (groupPrefix) container.querySelectorAll(`[id^="${groupPrefix}"]`).forEach(el => el.style.display='none');
  const target = document.getElementById(targetId);
  if (target) target.style.display = 'block';
}

/* ── COPY ────────────────────────────────────────────────── */
function copyToClipboard(text, label='Copié !') {
  navigator.clipboard?.writeText(text).then(() => toast(`📋 ${label}`, 'success'))
    .catch(() => { const ta=Object.assign(document.createElement('textarea'),{value:text,style:'position:fixed;opacity:0'});
      document.body.appendChild(ta); ta.select(); document.execCommand('copy'); document.body.removeChild(ta); toast(`📋 ${label}`,'success'); });
}
function copyPromo(el) { copyToClipboard(el.textContent.trim(), `Code ${el.textContent.trim()} copié !`); }

/* ── STAR RATING ─────────────────────────────────────────── */
function initStarRating(containerId, inputId) {
  const container = document.getElementById(containerId);
  const input     = document.getElementById(inputId);
  if (!container || !input) return;
  const stars = container.querySelectorAll('span');
  function apply(v) {
    input.value = v;
    stars.forEach((s,j) => { s.textContent = j<v?'★':'☆'; s.style.color = j<v?'var(--gold)':'var(--mut)'; });
  }
  stars.forEach((star, i) => {
    star.setAttribute('role','button'); star.setAttribute('tabindex','0');
    star.addEventListener('click', () => apply(i+1));
    star.addEventListener('keydown', e => { if(e.key==='Enter'||e.key===' ') apply(i+1); });
    star.addEventListener('mouseenter', () => stars.forEach((s,j) => s.style.color = j<=i?'var(--gold-lt)':'var(--mut)'));
    star.addEventListener('mouseleave', () => { const cur=parseInt(input.value)||0; stars.forEach((s,j) => s.style.color = j<cur?'var(--gold)':'var(--mut)'); });
  });
}

/* ── SLOT PICKER ─────────────────────────────────────────── */
function pickSlot(el) {
  if (el.classList.contains('taken')) return;
  document.querySelectorAll('.slot').forEach(s => s.classList.remove('picked'));
  el.classList.add('picked');
  const input = document.getElementById('selected-time');
  if (input) input.value = el.dataset.time || el.textContent.trim();
  navigator.vibrate?.(10);
}

/* ── SLOTS AJAX ──────────────────────────────────────────── */
async function loadSlots(shopId, serviceId, date) {
  const container = document.getElementById('slots-container');
  const input     = document.getElementById('selected-time');
  if (!container || !shopId || !serviceId || !date) return;
  container.innerHTML = '<div style="color:var(--mut);font-size:.84rem;padding:10px">⏳ Chargement…</div>';
  if (input) input.value = '';
  try {
    const res  = await apiFetch(`/bookings/creneaux/?shop=${shopId}&service=${serviceId}&date=${date}`);
    const data = await res.json();
    if (!data.slots?.length) { container.innerHTML = '<div style="color:var(--mut);font-size:.84rem;padding:10px">Aucun créneau disponible.</div>'; return; }
    const avail = data.slots.filter(s => s.available).length;
    container.innerHTML = `<div style="font-size:.75rem;color:var(--mut);margin-bottom:8px">${avail} créneau${avail!==1?'x':''} disponible${avail!==1?'s':''}</div>
      <div class="slots-grid">${data.slots.map(s =>`
        <div class="slot ${s.available?'':'taken'}" onclick="${s.available?'pickSlot(this)':''}"
          data-time="${s.time}" role="${s.available?'button':'presentation'}" tabindex="${s.available?0:-1}">
          ${s.time}
        </div>`).join('')}</div>`;
    container.querySelectorAll('.slot:not(.taken)').forEach(s =>
      s.addEventListener('keydown', e => { if(e.key==='Enter'||e.key===' '){ e.preventDefault(); pickSlot(s); } }));
  } catch {
    container.innerHTML = `<div style="color:var(--red);font-size:.84rem;padding:10px">Erreur. <button onclick="loadSlots('${shopId}','${serviceId}','${date}')" style="font-size:.78rem;margin-left:6px">Réessayer</button></div>`;
  }
}

/* ── FAVORITE ────────────────────────────────────────────── */
async function toggleFavAjax(btn, shopId) {
  if (btn.disabled) return;
  btn.disabled = true;
  const wasFav = btn.classList.contains('on');
  btn.innerHTML = wasFav ? '🤍' : '❤️'; btn.classList.toggle('on', !wasFav);
  try {
    const res  = await apiFetch(`/boutique/${shopId}/favori/`, { method: 'POST' });
    const data = await res.json();
    btn.innerHTML = data.is_favorite ? '❤️' : '🤍'; btn.classList.toggle('on', data.is_favorite);
    toast(data.is_favorite ? '❤️ Ajouté aux favoris !' : '💔 Retiré des favoris', data.is_favorite ? 'success' : 'default');
  } catch { btn.innerHTML = wasFav?'❤️':'🤍'; btn.classList.toggle('on', wasFav); toast('Erreur réseau', 'error'); }
  finally { btn.disabled = false; }
}

/* ── BOOKING ACTIONS ─────────────────────────────────────── */
async function cancelBooking(pk, btn) {
  if (!confirm('Annuler ce rendez-vous ?')) return;
  btn.disabled = true;
  try {
    const res  = await apiFetch(`/bookings/${pk}/annuler/`, { method: 'POST' });
    const data = await res.json();
    if (data.success) {
      const row   = btn.closest('tr') || btn.closest('.srv-item');
      const badge = row?.querySelector('.st');
      if (badge) { badge.className = 'st st-no'; badge.textContent = '✗ Annulé'; }
      btn.remove();
      toast('✅ Rendez-vous annulé', 'success');
    } else toast(data.error || 'Erreur', 'error');
  } catch { toast('Erreur réseau', 'error'); }
  finally { btn.disabled = false; }
}

async function confirmBooking(pk, btn) {
  btn.disabled = true;
  try {
    const res  = await apiFetch(`/bookings/${pk}/confirmer/`, { method: 'POST' });
    const data = await res.json();
    if (data.success) {
      const row   = btn.closest('tr');
      const badge = row?.querySelector('.st');
      if (badge) { badge.className = 'st st-ok'; badge.textContent = '✓ Confirmé'; }
      btn.closest('td')?.querySelectorAll('button').forEach(b => b.remove());
      toast('✅ Rendez-vous confirmé !', 'success');
    }
  } catch { toast('Erreur réseau', 'error'); }
  finally { btn.disabled = false; }
}

/* ── REVIEW SUBMIT ───────────────────────────────────────── */
async function submitReview(shopSlug) {
  const rating  = document.getElementById('review-rating')?.value;
  const comment = document.getElementById('review-comment')?.value?.trim();
  const title   = document.getElementById('review-title')?.value?.trim();
  if (!rating || rating === '0') { toast('⚠️ Veuillez choisir une note', 'warning'); return; }
  if (!comment) { toast('⚠️ Le commentaire est requis', 'warning'); return; }
  const btn = document.getElementById('submit-review-btn');
  const orig = btn?.textContent;
  if (btn) { btn.disabled = true; btn.textContent = 'Publication…'; }
  try {
    const res  = await apiFetch(`/reviews/boutique/${shopSlug}/avis/`, {
      method: 'POST', body: JSON.stringify({ rating: parseInt(rating), comment, title }),
    });
    const data = await res.json();
    if (data.success) { toast('⭐ Avis publié !', 'success'); closeOv('ov-review'); setTimeout(() => location.reload(), 1200); }
    else toast(data.error || 'Erreur', 'error');
  } catch { toast('Erreur réseau', 'error'); }
  finally { if (btn) { btn.disabled = false; btn.textContent = orig; } }
}

/* ── LIVE SEARCH ─────────────────────────────────────────── */
let _searchCtrl = null;
async function liveSearch(query) {
  const results = document.getElementById('search-results-dropdown');
  if (!results) return;
  if (!query || query.length < 2) { results.style.display = 'none'; return; }
  _searchCtrl?.abort(); _searchCtrl = new AbortController();
  results.innerHTML = '<div style="padding:10px;font-size:.84rem;color:var(--mut)">🔍 Recherche…</div>';
  results.style.display = 'block';
  try {
    const res  = await fetch(`/api/map-data/?q=${encodeURIComponent(query)}&limit=5`, { signal: _searchCtrl.signal });
    const data = await res.json();
    if (!data.shops?.length) { results.innerHTML = `<div style="padding:10px;font-size:.84rem;color:var(--mut)">Aucun résultat</div>`; return; }
    results.innerHTML = data.shops.map(s => `
      <a href="/boutique/${s.slug}/" style="display:flex;align-items:center;gap:10px;padding:10px 14px;border-bottom:1px solid rgba(255,255,255,.05);color:var(--txt);text-decoration:none;transition:background .2s" onmouseover="this.style.background='rgba(255,255,255,.04)'" onmouseout="this.style.background=''">
        <span style="font-size:1.2rem">${s.category_emoji||'🏪'}</span>
        <div>
          <div style="font-size:.875rem;font-weight:600;color:var(--parch)">${escapeHtml(s.name)}</div>
          <div style="font-size:.75rem;color:var(--mut)">${escapeHtml(s.quartier||'')}${s.rating?` · ⭐ ${s.rating}`:''}</div>
        </div>
      </a>`).join('');
  } catch(e) { if (e.name !== 'AbortError') results.innerHTML = '<div style="padding:10px;font-size:.84rem;color:var(--red)">Erreur de recherche</div>'; }
}

function submitSearch(e) {
  if (e) e.preventDefault();
  const q = document.getElementById('search-input')?.value?.trim();
  if (q) window.location.href = `/explorer/?q=${encodeURIComponent(q)}`;
}

/* ── MAP ─────────────────────────────────────────────────── */
let map = null, mapMarkers = [];
function initMap(shops = []) {
  const mapEl = document.getElementById('leaflet-map');
  if (!mapEl || !window.L) return;
  map = L.map('leaflet-map', { zoomControl: true }).setView([-4.2634, 15.2429], 12);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution:'© OSM', maxZoom:19 }).addTo(map);
  renderMapMarkers(shops);
}
function renderMapMarkers(shops = []) {
  mapMarkers.forEach(m => m.remove()); mapMarkers = [];
  if (!map || !shops.length) return;
  shops.forEach(s => {
    if (!s.lat || !s.lng) return;
    const icon = L.divIcon({ className:'', iconSize:[36,36], iconAnchor:[18,36],
      html:`<div style="width:36px;height:36px;border-radius:50% 50% 50% 0;background:var(--gold);display:flex;align-items:center;justify-content:center;font-size:1rem;transform:rotate(-45deg);box-shadow:0 4px 14px rgba(0,0,0,.5)"><span style="transform:rotate(45deg)">${s.category_emoji||'🏪'}</span></div>`,
    });
    const m = L.marker([s.lat, s.lng], { icon }).addTo(map).bindPopup(`
      <div class="map-popup">
        <div class="mp-name">${escapeHtml(s.name)}</div>
        <div class="mp-meta">${escapeHtml(s.get_quartier_display||s.quartier||'')}${s.rating?` · ⭐ ${s.rating}`:''}</div>
        <a href="/boutique/${s.slug}/" class="mp-btn">Voir la boutique →</a>
      </div>`);
    mapMarkers.push(m);
  });
  if (mapMarkers.length) {
    try { map.fitBounds(L.featureGroup(mapMarkers).getBounds().pad(.1)); } catch {}
  }
}
async function filterMap(cat, btn) {
  document.querySelectorAll('.map-pills .pill').forEach(p => p.classList.remove('on'));
  btn.classList.add('on');
  try {
    const res  = await apiFetch(`/api/map-data/?category=${encodeURIComponent(cat)}`);
    const data = await res.json();
    renderMapMarkers(data.shops || []);
  } catch { toast('Erreur chargement carte', 'error'); }
}

/* ── EXPLORE FILTER ──────────────────────────────────────── */
function filterExplore(cat, btn) {
  document.querySelectorAll('.explore-pills .pill').forEach(p => p.classList.remove('on'));
  btn.classList.add('on');
  const url = new URL(window.location);
  cat ? url.searchParams.set('category', cat) : url.searchParams.delete('category');
  url.searchParams.delete('page');
  window.location.href = url.toString();
}

/* ── COUNTERS ────────────────────────────────────────────── */
function animateCounters() {
  const obs = new IntersectionObserver((entries) => {
    entries.forEach(({ target, isIntersecting }) => {
      if (!isIntersecting || target.dataset.animated) return;
      target.dataset.animated = '1';
      const max = parseInt(target.dataset.count), suf = target.dataset.suffix||'';
      let cur = 0; const step = Math.ceil(max/60);
      const iv = setInterval(() => { cur = Math.min(cur+step, max); target.textContent = cur.toLocaleString('fr-FR')+suf; if (cur>=max) clearInterval(iv); }, 22);
    });
  }, { threshold: 0.3 });
  document.querySelectorAll('[data-count]').forEach(el => obs.observe(el));
}

/* ── DASHBOARD TABS ──────────────────────────────────────── */
function dashTab(tab, btn) {
  document.querySelectorAll('.sb-item').forEach(i => i.classList.remove('on'));
  btn?.classList.add('on');
  const url = new URL(window.location);
  url.searchParams.set('tab', tab);
  history.pushState({ tab }, '', url.toString());
  window.location.href = url.toString();  // full reload for simplicity
}

/* ── NOTIF BADGE ─────────────────────────────────────────── */
async function loadNotifCount() {
  try {
    const res  = await fetch('/notifications/json/');
    if (!res.ok) return;
    const data = await res.json();
    const unread = data.notifications.filter(n => !n.is_read).length;
    document.querySelectorAll('.notif-count-badge').forEach(b => {
      b.textContent = unread; b.style.display = unread ? 'inline' : 'none';
    });
  } catch {}
}

/* ── WEBSOCKET CHAT ──────────────────────────────────────── */
let ws = null, _wsConvId = null, _wsDelay = 1000;

function initWebSocket(convId) {
  if (!convId) return;
  _wsConvId = convId;
  const proto = location.protocol === 'https:' ? 'wss' : 'ws';
  ws = new WebSocket(`${proto}://${location.host}/ws/chat/${convId}/`);
  ws.onopen  = () => { _wsDelay = 1000; };
  ws.onclose = () => { setTimeout(() => initWebSocket(_wsConvId), _wsDelay); _wsDelay = Math.min(_wsDelay*1.5, 30000); };
  ws.onmessage = e => {
    try {
      const d = JSON.parse(e.data);
      if (d.type === 'chat_message') {
        const msg = d.message;
        const me  = parseInt(document.getElementById('current-user-id')?.value||0);
        if (msg.sender_id !== me) appendMessage(msg.content, false, msg.sender_initials, msg.created_at);
      }
    } catch {}
  };
}

function sendWsMessage(convId) {
  const inp = document.getElementById('chat-input');
  if (!inp?.value.trim()) return;
  const content = inp.value.trim();
  if (ws?.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: 'message', content }));
    appendMessage(content, true, '', new Date().toLocaleTimeString('fr-FR',{hour:'2-digit',minute:'2-digit'}));
    inp.value = '';
  } else sendMessageHttp(convId);
}

async function sendMessageHttp(convId) {
  const inp = document.getElementById('chat-input');
  if (!inp?.value.trim()) return;
  const content = inp.value.trim(); inp.value = '';
  try {
    const res  = await apiFetch(`/messages/${convId}/envoyer/`, { method:'POST', body: JSON.stringify({content}) });
    const data = await res.json();
    if (data.success) appendMessage(data.message.content, true, '', data.message.created_at);
  } catch { toast('Message non envoyé', 'error'); }
}

function appendMessage(content, isMine, initials, time) {
  const box = document.getElementById('chat-box'); if (!box) return;
  const div = document.createElement('div');
  div.style.cssText = `display:flex;flex-direction:column;${isMine?'align-items:flex-end':'align-items:flex-start'}`;
  div.innerHTML = `<div class="cm ${isMine?'me':'them'}">${escapeHtml(content)}</div><div class="cm-time">${escapeHtml(String(time))}</div>`;
  box.appendChild(div);
  box.scrollTo({ top: box.scrollHeight, behavior: 'smooth' });
}

/* ── UTILS ───────────────────────────────────────────────── */
function escapeHtml(s) {
  if (s==null) return '';
  return String(s).replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
}
const debounce = (fn, ms) => { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; };
function formatPrice(n) { return new Intl.NumberFormat('fr-FR').format(n) + ' FCFA'; }

/* ── PULL-TO-REFRESH ─────────────────────────────────────── */
function initPullToRefresh() {
  let startY = 0, pulling = false;
  const ind = document.getElementById('ptr-indicator');
  document.addEventListener('touchstart', e => { if (!window.scrollY) startY = e.touches[0].clientY; }, { passive:true });
  document.addEventListener('touchmove',  e => {
    const d = e.touches[0].clientY - startY;
    if (d > 0 && !window.scrollY && !pulling) { pulling = true; if(ind) ind.style.display='flex'; }
    if (ind && pulling) ind.style.opacity = Math.min(d/80, 1);
  }, { passive:true });
  document.addEventListener('touchend', e => {
    const d = e.changedTouches[0].clientY - startY;
    if (pulling && d > 80) window.location.reload();
    else if (ind) { ind.style.display='none'; ind.style.opacity=0; }
    pulling = false; startY = 0;
  }, { passive:true });
}

/* ── INIT ────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  if (document.querySelector('[data-count]')) animateCounters();
  if (document.getElementById('star-container')) initStarRating('star-container','review-rating');

  // Slots
  const dateInp = document.getElementById('booking-date');
  const svcInp  = document.getElementById('booking-service');
  const shopId  = document.getElementById('booking-shop-id')?.value;
  const refresh = () => { if (shopId && svcInp?.value && dateInp?.value) loadSlots(shopId, svcInp.value, dateInp.value); };
  dateInp?.addEventListener('change', refresh);
  svcInp?.addEventListener('change',  refresh);

  // Live search
  const srch = document.getElementById('search-input');
  if (srch) {
    const dbs = debounce(liveSearch, 300);
    srch.addEventListener('input', e => dbs(e.target.value));
    srch.addEventListener('keypress', e => { if (e.key==='Enter') submitSearch(e); });
    document.addEventListener('click', e => { if (!srch.contains(e.target)) { const d=document.getElementById('search-results-dropdown'); if(d) d.style.display='none'; } });
  }

  // Chat
  document.getElementById('chat-input')?.addEventListener('keypress', e => {
    if (e.key==='Enter' && !e.shiftKey) { e.preventDefault(); const c=document.getElementById('conv-id')?.value; if(c) sendWsMessage(c); }
  });
  const chatBox = document.getElementById('chat-box');
  if (chatBox) chatBox.scrollTop = chatBox.scrollHeight;

  // Carte
  const mapEl = document.getElementById('leaflet-map');
  if (mapEl) {
    const shops = JSON.parse(document.getElementById('shops-json-data')?.textContent||'[]');
    if (window.L) initMap(shops);
    else {
      const link = document.createElement('link'); link.rel='stylesheet'; link.href='https://unpkg.com/leaflet@1.9.4/dist/leaflet.css'; document.head.appendChild(link);
      const sc = document.createElement('script'); sc.src='https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'; sc.onload = () => initMap(shops); document.head.appendChild(sc);
    }
  }

  // WS
  const convId = document.getElementById('conv-id')?.value;
  if (convId) initWebSocket(convId);

  // Badge notifs
  if (document.body.dataset.authenticated === 'true') {
    loadNotifCount();
    setInterval(loadNotifCount, 60_000);
  }

  // Pull-to-refresh
  if ('ontouchstart' in window) initPullToRefresh();
});

/* ============================================================
   BEAUTYMAP CONGO — posts.js
   Gestion complète des publications du dashboard pro
   ============================================================ */

/* ── Variables globales ── */
let _postFiles = [];

/* ── Sélection du type de publication ── */
function selectPostType(btn) {
  document.querySelectorAll('#post-type-pills .pill').forEach(p => p.classList.remove('on'));
  btn.classList.add('on');
  document.getElementById('selected-post-type').value = btn.dataset.type;
}

/* ── Preview des images ── */
function previewPostImages(files) {
  _postFiles = Array.from(files).slice(0, 10);
  _renderPreviews();
}

function handlePostDrop(e) {
  e.preventDefault();
  e.currentTarget.style.borderColor = 'rgba(201,151,58,.35)';
  _postFiles = Array.from(e.dataTransfer.files)
    .filter(f => f.type.startsWith('image/'))
    .slice(0, 10);
  _renderPreviews();
}

function _renderPreviews() {
  const container = document.getElementById('post-photos-preview');
  if (!container) return;
  container.innerHTML = '';
  _postFiles.forEach((file, i) => {
    const reader = new FileReader();
    reader.onload = e => {
      const wrap = document.createElement('div');
      wrap.style.cssText = 'position:relative;width:80px;height:80px;border-radius:8px;overflow:hidden;flex-shrink:0';
      wrap.innerHTML = `
        <img src="${e.target.result}" style="width:100%;height:100%;object-fit:cover">
        <button type="button" onclick="removePostImage(${i})"
          style="position:absolute;top:2px;right:2px;background:rgba(0,0,0,.75);border:none;
                 color:#fff;width:20px;height:20px;border-radius:50%;cursor:pointer;
                 font-size:.7rem;display:flex;align-items:center;justify-content:center;
                 line-height:1">✕</button>`;
      container.appendChild(wrap);
    };
    reader.readAsDataURL(file);
  });

  /* Mettre à jour le texte de la zone de drop */
  const hint = document.querySelector('#post-drop-zone > div:last-child');
  if (hint) hint.textContent = _postFiles.length
    ? `${_postFiles.length} photo${_postFiles.length > 1 ? 's' : ''} sélectionnée${_postFiles.length > 1 ? 's' : ''}`
    : '📷 Cliquez ou glissez vos photos ici';
}

function removePostImage(index) {
  _postFiles.splice(index, 1);
  _renderPreviews();
}

/* ── Publier un post ── */
async function publishPost(shopSlug) {
  const caption  = document.getElementById('post-caption')?.value?.trim() || '';
  const postType = document.getElementById('selected-post-type')?.value || 'realisation';
  const price    = document.getElementById('post-price')?.value || '';

  if (!caption && _postFiles.length === 0) {
    toast('⚠️ Ajoutez une description ou une photo', 'warning');
    return;
  }

  const btn = document.getElementById('publish-btn');
  const origText = btn?.textContent;
  if (btn) { btn.disabled = true; btn.textContent = '⏳ Publication en cours…'; }

  const formData = new FormData();
  formData.append('caption',   caption);
  formData.append('post_type', postType);
  if (price) formData.append('price', price);
  _postFiles.forEach(f => formData.append('images', f));

  try {
    const res  = await fetch(`/boutique/${shopSlug}/publier/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': getCsrfToken() },
      body: formData,
    });
    const data = await res.json();

    if (data.success) {
      toast('🎉 Publication créée avec succès !', 'success');
      closeOv('ov-new-post');

      /* Reset complet du formulaire */
      if (document.getElementById('post-caption')) document.getElementById('post-caption').value = '';
      if (document.getElementById('post-price'))   document.getElementById('post-price').value   = '';
      if (document.getElementById('post-photos-preview')) document.getElementById('post-photos-preview').innerHTML = '';
      _postFiles = [];
      document.querySelectorAll('#post-type-pills .pill').forEach((p, i) => p.classList.toggle('on', i === 0));
      document.getElementById('selected-post-type').value = 'realisation';

      /* Recharger la page pour voir la nouvelle publication */
      setTimeout(() => window.location.reload(), 900);
    } else {
      toast(data.error || 'Erreur lors de la publication', 'error');
    }
  } catch (err) {
    toast('Erreur réseau — vérifiez votre connexion', 'error');
  } finally {
    if (btn) { btn.disabled = false; btn.textContent = origText; }
  }
}

/* ── Supprimer un post ── */
async function deletePost(postId, btn) {
  if (!confirm('Supprimer cette publication définitivement ?')) return;
  btn.disabled = true;
  try {
    const res  = await fetch(`/post/${postId}/supprimer/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': getCsrfToken() },
    });
    const data = await res.json();
    if (data.success) {
      /* Supprimer la card du DOM */
      const card = document.querySelector(`[data-post-id="${postId}"]`);
      if (card) {
        card.style.transition = 'opacity .3s, transform .3s';
        card.style.opacity    = '0';
        card.style.transform  = 'scale(.95)';
        setTimeout(() => card.remove(), 300);
      }
      toast('🗑️ Publication supprimée', 'success');
    } else {
      toast(data.error || 'Erreur lors de la suppression', 'error');
    }
  } catch {
    toast('Erreur réseau', 'error');
  } finally {
    btn.disabled = false;
  }
}

/* ── Like (depuis la page Découverte) ── */
async function toggleLike(btn, postId) {
  if (document.body.dataset.authenticated !== 'true') {
    window.location.href = '/auth/login/?next=/decouverte/';
    return;
  }
  if (btn.disabled) return;
  btn.disabled = true;
  try {
    const res  = await fetch(`/post/${postId}/like/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': getCsrfToken() },
    });
    const data = await res.json();
    const heart = btn.querySelector('.heart');
    const count = btn.querySelector('.like-count');
    if (heart) heart.textContent = data.liked ? '❤️' : '🤍';
    if (count) count.textContent = data.count;
    btn.classList.toggle('liked', data.liked);
    btn.style.color = data.liked ? 'var(--red)' : 'var(--mut)';
  } catch {
    toast('Erreur réseau', 'error');
  } finally {
    btn.disabled = false;
  }
}

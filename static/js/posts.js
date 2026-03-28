/* ============================================================
   BEAUTYMAP CONGO — posts.js
   À inclure dans le dashboard pro (ou à la fin de main.js)
   ============================================================ */

/* ── Sélection du type de post ── */
function selectPostType(btn) {
  document.querySelectorAll('#post-type-pills .pill').forEach(p => p.classList.remove('on'));
  btn.classList.add('on');
  document.getElementById('selected-post-type').value = btn.dataset.type;
}

/* ── Preview des images sélectionnées ── */
let _postFiles = [];

function previewPostImages(files) {
  _postFiles = Array.from(files);
  renderPostPreviews();
}

function handlePostDrop(e) {
  e.preventDefault();
  e.currentTarget.style.borderColor = 'rgba(201,151,58,.35)';
  _postFiles = Array.from(e.dataTransfer.files).filter(f => f.type.startsWith('image/')).slice(0, 10);
  renderPostPreviews();
}

function renderPostPreviews() {
  const container = document.getElementById('post-photos-preview');
  container.innerHTML = '';
  _postFiles.forEach((file, i) => {
    const reader = new FileReader();
    reader.onload = e => {
      const wrap = document.createElement('div');
      wrap.style.cssText = 'position:relative;width:80px;height:80px;border-radius:8px;overflow:hidden';
      wrap.innerHTML = `
        <img src="${e.target.result}" style="width:100%;height:100%;object-fit:cover">
        <button onclick="removePostImage(${i})" style="position:absolute;top:2px;right:2px;
          background:rgba(0,0,0,.7);border:none;color:#fff;width:18px;height:18px;
          border-radius:50%;cursor:pointer;font-size:.7rem;display:flex;align-items:center;justify-content:center">✕</button>`;
      container.appendChild(wrap);
    };
    reader.readAsDataURL(file);
  });
}

function removePostImage(index) {
  _postFiles.splice(index, 1);
  renderPostPreviews();
}

/* ── Publier un post ── */
async function publishPost(shopSlug) {
  const caption  = document.getElementById('post-caption')?.value.trim();
  const postType = document.getElementById('selected-post-type')?.value;
  const price    = document.getElementById('post-price')?.value;

  if (!caption && _postFiles.length === 0) {
    toast('⚠️ Ajoutez une description ou une photo', 'warning');
    return;
  }

  const btn = document.getElementById('publish-btn');
  btn.disabled = true;
  btn.textContent = '⏳ Publication…';

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
      toast('🎉 Publication créée !', 'success');
      closeOv('ov-new-post');
      // Reset du formulaire
      document.getElementById('post-caption').value = '';
      document.getElementById('post-price').value   = '';
      document.getElementById('post-photos-preview').innerHTML = '';
      _postFiles = [];
      // Recharger la page pour voir la nouvelle publication
      setTimeout(() => window.location.reload(), 800);
    } else {
      toast(data.error || 'Erreur lors de la publication', 'error');
    }
  } catch {
    toast('Erreur réseau', 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = '📤 Publier';
  }
}

/* ── Supprimer un post ── */
async function deletePost(postId, btn) {
  if (!confirm('Supprimer cette publication définitivement ?')) return;
  btn.disabled = true;
  try {
    const res  = await fetch(`/post/${postId}/supprimer/`, {
      method: 'POST', headers: { 'X-CSRFToken': getCsrfToken() }
    });
    const data = await res.json();
    if (data.success) {
      btn.closest('[data-post-id], div[style]')?.remove();
      toast('🗑️ Publication supprimée', 'success');
    }
  } catch {
    toast('Erreur réseau', 'error');
  } finally {
    btn.disabled = false;
  }
}

/* ── Like (depuis la page Découverte) ── */
async function toggleLike(btn, postId) {
  if (!document.body.dataset.authenticated === 'true') {
    window.location.href = '/auth/login/?next=/decouverte/';
    return;
  }
  btn.disabled = true;
  try {
    const res  = await fetch(`/post/${postId}/like/`, {
      method: 'POST', headers: { 'X-CSRFToken': getCsrfToken() }
    });
    const data = await res.json();
    const heart = btn.querySelector('.heart');
    const count = btn.querySelector('.like-count');
    if (heart) heart.textContent = data.liked ? '❤️' : '🤍';
    if (count) count.textContent = data.count;
    btn.classList.toggle('liked', data.liked);
  } catch {
    toast('Erreur réseau', 'error');
  } finally {
    btn.disabled = false;
  }
}

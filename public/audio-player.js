// ============================================================
// audio-player.js - Lecteur audio (mini-player, seek, toggle, etc.)
// Extrait de map_logic.js pour meilleure lisibilité
// ============================================================

// État du mini-player (type Spotify)
let _currentPlaying = null; // { prefix, itemId, trackIndex, title, subtitle }

function formatAudioTime(seconds) {
  if (!seconds || isNaN(seconds) || !isFinite(seconds)) return '0:00';
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return m + ':' + (s < 10 ? '0' : '') + s;
}

function seekAudio(prefix, itemId, trackIndex, ev) {
  const audio = document.getElementById(`${prefix}-audio-${itemId}-${trackIndex}`);
  const progBar = document.getElementById(`progress-${prefix}-${itemId}-${trackIndex}`);
  const seekBar = document.getElementById(`seekbar-${prefix}-${itemId}-${trackIndex}`);
  if (!audio || !seekBar) return;
  const rect = seekBar.getBoundingClientRect();
  const clientX = ev.touches ? ev.touches[0].clientX : ev.clientX;
  const pct = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
  if (audio.duration && !isNaN(audio.duration)) {
    audio.currentTime = pct * audio.duration;
  } else {
    audio.load();
    audio.addEventListener('loadedmetadata', function onMeta() {
      audio.removeEventListener('loadedmetadata', onMeta);
      if (audio.duration && !isNaN(audio.duration)) {
        audio.currentTime = pct * audio.duration;
      }
      updateAudioTimeDisplay(prefix, itemId, trackIndex);
    }, { once: true });
  }
  if (progBar) progBar.style.width = (100 * pct) + '%';
  updateAudioTimeDisplay(prefix, itemId, trackIndex);
}

function startAudioDrag(prefix, itemId, trackIndex, ev) {
  ev.preventDefault();
  ev.stopPropagation();
  _audioDragging = { prefix, itemId, trackIndex };
  seekAudio(prefix, itemId, trackIndex, ev);
}

function updateAudioTimeDisplay(prefix, itemId, trackIndex) {
  const audio = document.getElementById(`${prefix}-audio-${itemId}-${trackIndex}`);
  const timeEl = document.getElementById(`time-${prefix}-${itemId}-${trackIndex}`);
  if (!audio || !timeEl) return;
  const current = formatAudioTime(audio.currentTime);
  const total = formatAudioTime(audio.duration);
  timeEl.textContent = current + ' / ' + total;
}

// Drag global handlers (mouse + touch)
document.addEventListener('mousemove', function(ev) {
  if (!_audioDragging) return;
  seekAudio(_audioDragging.prefix, _audioDragging.itemId, _audioDragging.trackIndex, ev);
});
document.addEventListener('mouseup', function() { _audioDragging = null; });
document.addEventListener('touchmove', function(ev) {
  if (!_audioDragging) return;
  seekAudio(_audioDragging.prefix, _audioDragging.itemId, _audioDragging.trackIndex, ev);
}, { passive: false });
document.addEventListener('touchend', function() { _audioDragging = null; });

function showMiniPlayer(prefix, itemId, trackIndex, title, subtitle) {
  _currentPlaying = { prefix, itemId, trackIndex, title: title || '—', subtitle: subtitle || 'Piste ' + (trackIndex + 1) };
  const el = document.getElementById('audio-mini-player');
  if (!el) return;
  el.classList.add('visible');
  document.getElementById('mini-player-title').textContent = _currentPlaying.title;
  document.getElementById('mini-player-subtitle').textContent = _currentPlaying.subtitle;
  updateMiniPlayerUI();
}

function hideMiniPlayer() {
  _currentPlaying = null;
  const el = document.getElementById('audio-mini-player');
  if (el) el.classList.remove('visible');
}

// Ouvrir la popup de l'artiste/event en cours d'écoute
function openCurrentPlayingPopup() {
  if (!_currentPlaying) return;
  const { prefix, itemId } = _currentPlaying;
  // Déterminer le type à partir du préfixe audio (booking, event, service)
  const type = prefix;
  const numId = parseInt(itemId);
  
  // Trouver l'item dans les données
  const dataArr = type === 'booking' ? bookingsData : type === 'event' ? eventsData : servicesData;
  const item = dataArr.find(i => i.id === numId);
  
  if (item) {
    // Ouvrir la popup de l'item (même fonction que le clic depuis la liste)
    if (typeof openPopupFromList === 'function') {
      openPopupFromList(type, numId);
    }
  } else {
    showNotification("L'artiste n'est plus visible sur la carte. Rapprochez-vous de sa position.", "info");
  }
}
window.openCurrentPlayingPopup = openCurrentPlayingPopup;

function updateMiniPlayerUI() {
  if (!_currentPlaying) return;
  const { prefix, itemId, trackIndex } = _currentPlaying;
  const audio = document.getElementById(`${prefix}-audio-${itemId}-${trackIndex}`);
  const timeEl = document.getElementById('mini-player-time');
  const playBtn = document.getElementById('mini-player-play');
  if (!audio) return;
  if (timeEl) timeEl.textContent = formatAudioTime(audio.currentTime) + ' / ' + formatAudioTime(audio.duration);
  if (playBtn) playBtn.innerHTML = audio.paused ? '▶' : '⏸';
}

function seekAudioOffset(prefix, itemId, trackIndex, deltaSeconds) {
  const audio = document.getElementById(`${prefix}-audio-${itemId}-${trackIndex}`);
  const progBar = document.getElementById(`progress-${prefix}-${itemId}-${trackIndex}`);
  if (!audio) return;
  let t = audio.currentTime + deltaSeconds;
  t = Math.max(0, Math.min(audio.duration || 0, t));
  audio.currentTime = t;
  if (progBar && audio.duration) progBar.style.width = (100 * t / audio.duration) + '%';
  updateAudioTimeDisplay(prefix, itemId, trackIndex);
  updateMiniPlayerUI();
}

async function toggleAudioGeneric(prefix, itemId, trackIndex) {
  if (navigator.vibrate) navigator.vibrate(10);
  const audio = document.getElementById(`${prefix}-audio-${itemId}-${trackIndex}`);
  const btn = document.getElementById(`btn-${prefix}-${itemId}-${trackIndex}`);
  const progressBar = document.getElementById(`progress-${prefix}-${itemId}-${trackIndex}`);
  const container = document.querySelector(`[data-audio-track] [id="btn-${prefix}-${itemId}-${trackIndex}"]`)?.closest('[data-audio-track]');
  const title = container?.getAttribute('data-item-title') || '—';
  const subtitle = container?.getAttribute('data-track-label') || ('Piste ' + (trackIndex + 1));
  if (!audio) return;
  
  if (audio.paused) {
    // Mode hors-ligne : utiliser le cache si disponible
    const originalUrl = audio.getAttribute('data-original-src') || audio.src;
    if (!navigator.onLine && window.indexedDBService?.getAudioCache) {
      try {
        const blobUrl = await window.indexedDBService.getAudioCache(originalUrl);
        if (blobUrl) audio.src = blobUrl;
      } catch (_) {}
    }
    // Stopper les autres audios (booking + event)
    // Couper UNIQUEMENT les autres sons (pas celui qu'on lance) - un seul son à la fois
    document.querySelectorAll('audio[id^="booking-audio-"], audio[id^="event-audio-"]').forEach(a => {
      if (a !== audio) { a.pause(); a.currentTime = 0; }
    });
    document.querySelectorAll('[id^="progress-booking-"], [id^="progress-event-"]').forEach(p => {
      if (p !== progressBar) p.style.width = '0%';
    });
    document.querySelectorAll('[id^="btn-booking-"], [id^="btn-event-"]').forEach(b => {
      if (b !== btn) b.innerHTML = '▶';
    });
    // Reset tous les time displays
    document.querySelectorAll('[id^="time-booking-"], [id^="time-event-"]').forEach(t => {
      const tid = t.id;
      if (!tid.includes(`${prefix}-${itemId}-${trackIndex}`)) t.textContent = '0:00';
    });
    
    audio.play();
    if (btn) btn.innerHTML = '⏸';
    showMiniPlayer(prefix, itemId, trackIndex, title, subtitle);
    // Cache pour mode hors-ligne (après chargement)
    const origUrl = audio.getAttribute('data-original-src') || audio.src;
    if (navigator.onLine && origUrl && window.indexedDBService?.setAudioCache && !origUrl.startsWith('blob:')) {
      audio.oncanplay = async () => {
        audio.oncanplay = null;
        try {
          const r = await fetch(origUrl, { mode: 'cors' });
          if (r.ok) {
            const blob = await r.blob();
            await window.indexedDBService.setAudioCache(origUrl, blob);
          }
        } catch (_) {}
      };
    }
    audio.onended = () => {
      if (btn) btn.innerHTML = '▶';
      if (progressBar) progressBar.style.width = '0%';
      updateAudioTimeDisplay(prefix, itemId, trackIndex);
      hideMiniPlayer();
    };
    audio.ontimeupdate = () => {
      if (_audioDragging) return;
      if (progressBar && audio.duration) {
        progressBar.style.width = (100 * audio.currentTime / audio.duration) + '%';
      }
      updateAudioTimeDisplay(prefix, itemId, trackIndex);
      updateMiniPlayerUI();
    };
  } else {
    audio.pause();
    if (btn) btn.innerHTML = '▶';
    hideMiniPlayer();
  }
}

function toggleBookingAudio(bookingId, trackIndex) {
  toggleAudioGeneric('booking', bookingId, trackIndex);
}
function toggleEventAudio(eventId, trackIndex) {
  toggleAudioGeneric('event', eventId, trackIndex);
}

window.toggleBookingAudio = toggleBookingAudio;
window.toggleEventAudio = toggleEventAudio;
window.seekBookingAudio = (id, i, ev) => seekAudio('booking', id, i, ev);
window.seekEventAudio = (id, i, ev) => seekAudio('event', id, i, ev);
window.startAudioDrag = startAudioDrag;
window.seekAudioOffset = seekAudioOffset;

// Initialiser les boutons du mini-player (après chargement DOM)
function initMiniPlayerButtons() {
  const playBtn = document.getElementById('mini-player-play');
  const rewindBtn = document.getElementById('mini-player-rewind');
  const forwardBtn = document.getElementById('mini-player-forward');
  if (playBtn) playBtn.onclick = () => {
    if (!_currentPlaying) return;
    const { prefix, itemId, trackIndex } = _currentPlaying;
    toggleAudioGeneric(prefix, itemId, trackIndex);
  };
  if (rewindBtn) rewindBtn.onclick = () => {
    if (!_currentPlaying) return;
    seekAudioOffset(_currentPlaying.prefix, _currentPlaying.itemId, _currentPlaying.trackIndex, -15);
    if (navigator.vibrate) navigator.vibrate(10);
  };
  if (forwardBtn) forwardBtn.onclick = () => {
    if (!_currentPlaying) return;
    seekAudioOffset(_currentPlaying.prefix, _currentPlaying.itemId, _currentPlaying.trackIndex, 15);
    if (navigator.vibrate) navigator.vibrate(10);
  };
}
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initMiniPlayerButtons);
} else {
  initMiniPlayerButtons();
}

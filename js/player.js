// ============================================================
// PLAYER.JS — پلیر صوتی حرفه‌ای
// ============================================================

const Player = (() => {
  const audio = document.getElementById('main-audio');
  const wrap = document.getElementById('audio-player-wrap');
  const playIcon = document.getElementById('play-icon');
  const progressFill = document.getElementById('progress-fill');
  const progressThumb = document.getElementById('progress-thumb');
  const progressBar = document.getElementById('progress-bar');
  const currentTimeEl = document.getElementById('current-time');
  const totalTimeEl = document.getElementById('total-time');
  const volSlider = document.getElementById('volume-slider');
  const volIcon = document.getElementById('vol-icon');
  const speedLabel = document.getElementById('speed-label');
  const playerTitle = document.getElementById('player-book-title');
  const playerChapter = document.getElementById('player-chapter');
  const playerCover = document.getElementById('player-cover-img');
  const sleepPopup = document.getElementById('sleep-popup');
  const speedPopup = document.getElementById('speed-popup');

  let sleepTimer = null;
  let bookmarks = JSON.parse(localStorage.getItem('ssa_bookmarks') || '[]');
  let currentBook = null;
  let currentChapter = null;
  let isDragging = false;

  function formatTime(sec) {
    if (isNaN(sec)) return '۰:۰۰';
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    const toFa = n => n.toString().replace(/\d/g, d => '۰۱۲۳۴۵۶۷۸۹'[d]);
    return `${toFa(m)}:${toFa(s).padStart(2, '۰')}`;
  }

  function play(book, chapterIndex = 0) {
    currentBook = book;
    currentChapter = chapterIndex;
    const ch = book.chapters[chapterIndex];

    playerTitle.textContent = book.title;
    playerChapter.textContent = ch.title;
    playerCover.src = book.cover;
    playerCover.alt = book.title;

    if (ch.src && ch.src !== "") {
      audio.src = ch.src;
    } else {
      // Demo mode — use a silent audio for UI demo
      audio.src = "";
    }

    wrap.style.display = 'flex';
    wrap.classList.add('player-visible');

    audio.play().then(() => {
      setPlayIcon(true);
    }).catch(() => {
      setPlayIcon(false);
    });

    updateMediaSession(book, ch);
  }

  function setPlayIcon(playing) {
    playIcon.className = playing ? 'fa-solid fa-pause' : 'fa-solid fa-play';
  }

  function updateMediaSession(book, ch) {
    if ('mediaSession' in navigator) {
      navigator.mediaSession.metadata = new MediaMetadata({
        title: book.title,
        artist: book.author,
        album: ch.title,
        artwork: [{ src: book.cover, sizes: '512x512', type: 'image/jpeg' }]
      });
      navigator.mediaSession.setActionHandler('play', () => audio.play());
      navigator.mediaSession.setActionHandler('pause', () => audio.pause());
    }
  }

  // Event: timeupdate
  audio.addEventListener('timeupdate', () => {
    if (isDragging) return;
    const pct = audio.duration ? (audio.currentTime / audio.duration) * 100 : 0;
    progressFill.style.width = pct + '%';
    progressThumb.style.left = pct + '%';
    currentTimeEl.textContent = formatTime(audio.currentTime);
    totalTimeEl.textContent = formatTime(audio.duration);
  });

  audio.addEventListener('play', () => setPlayIcon(true));
  audio.addEventListener('pause', () => setPlayIcon(false));
  audio.addEventListener('ended', () => {
    setPlayIcon(false);
    // auto-advance to next chapter
    if (currentBook && currentChapter < currentBook.chapters.length - 1) {
      play(currentBook, currentChapter + 1);
    }
  });

  // Play/Pause
  document.getElementById('btn-play-pause').addEventListener('click', () => {
    if (audio.src && audio.src !== window.location.href) {
      audio.paused ? audio.play() : audio.pause();
    } else {
      showToast('فایل صوتی در حال حاضر موجود نیست', 'info');
    }
  });

  // Rewind / Forward
  document.getElementById('btn-rewind').addEventListener('click', () => { audio.currentTime -= 15; });
  document.getElementById('btn-forward').addEventListener('click', () => { audio.currentTime += 15; });

  // Progress bar drag
  function seekTo(e) {
    const rect = progressBar.getBoundingClientRect();
    const x = (e.clientX || e.touches?.[0]?.clientX) - rect.left;
    const pct = Math.max(0, Math.min(1, x / rect.width));
    if (audio.duration) {
      audio.currentTime = pct * audio.duration;
    }
  }

  progressBar.addEventListener('mousedown', (e) => { isDragging = true; seekTo(e); });
  progressBar.addEventListener('touchstart', (e) => { isDragging = true; seekTo(e); }, { passive: true });
  document.addEventListener('mousemove', (e) => { if (isDragging) seekTo(e); });
  document.addEventListener('touchmove', (e) => { if (isDragging) seekTo(e); }, { passive: true });
  document.addEventListener('mouseup', () => { isDragging = false; });
  document.addEventListener('touchend', () => { isDragging = false; });

  // Volume
  volSlider.addEventListener('input', () => {
    audio.volume = volSlider.value;
    updateVolIcon();
  });

  document.getElementById('btn-mute').addEventListener('click', () => {
    audio.muted = !audio.muted;
    updateVolIcon();
  });

  function updateVolIcon() {
    const v = audio.muted ? 0 : audio.volume;
    volIcon.className = v === 0 ? 'fa-solid fa-volume-xmark' : v < 0.5 ? 'fa-solid fa-volume-low' : 'fa-solid fa-volume-high';
  }

  // Speed
  document.getElementById('btn-speed').addEventListener('click', (e) => {
    e.stopPropagation();
    sleepPopup.style.display = 'none';
    speedPopup.style.display = speedPopup.style.display === 'none' ? 'flex' : 'none';
  });

  window.setSpeed = function(s) {
    audio.playbackRate = s;
    const toFa = n => n.toString().replace(/\d/g, d => '۰۱۲۳۴۵۶۷۸۹'[d]);
    speedLabel.textContent = toFa(s) + '×';
    speedPopup.querySelectorAll('button').forEach(b => b.classList.remove('active'));
    [...speedPopup.querySelectorAll('button')].find(b => parseFloat(b.textContent) === s)?.classList.add('active');
    speedPopup.style.display = 'none';
  };

  // Sleep timer
  document.getElementById('btn-sleep').addEventListener('click', (e) => {
    e.stopPropagation();
    speedPopup.style.display = 'none';
    sleepPopup.style.display = sleepPopup.style.display === 'none' ? 'block' : 'none';
  });

  window.setSleep = function(min) {
    if (sleepTimer) clearTimeout(sleepTimer);
    sleepPopup.style.display = 'none';
    if (min === 0) { showToast('تایمر خواب لغو شد', 'info'); return; }
    sleepTimer = setTimeout(() => { audio.pause(); showToast('پخش متوقف شد ⏰', 'info'); }, min * 60000);
    const toFa = n => n.toString().replace(/\d/g, d => '۰۱۲۳۴۵۶۷۸۹'[d]);
    showToast(`پخش بعد از ${toFa(min)} دقیقه متوقف می‌شود`, 'success');
  };

  // Bookmark
  document.getElementById('btn-bookmark').addEventListener('click', () => {
    if (!currentBook) return;
    const bm = {
      bookId: currentBook.id,
      bookTitle: currentBook.title,
      chapter: currentChapter,
      time: audio.currentTime,
      label: formatTime(audio.currentTime)
    };
    bookmarks.push(bm);
    localStorage.setItem('ssa_bookmarks', JSON.stringify(bookmarks));
    document.getElementById('btn-bookmark').querySelector('i').className = 'fa-solid fa-bookmark';
    showToast('بوکمارک ذخیره شد 🔖', 'success');
    setTimeout(() => {
      document.getElementById('btn-bookmark').querySelector('i').className = 'fa-regular fa-bookmark';
    }, 2000);
  });

  // Close player
  document.getElementById('btn-close-player').addEventListener('click', () => {
    audio.pause();
    wrap.classList.remove('player-visible');
    setTimeout(() => { wrap.style.display = 'none'; }, 400);
  });

  // Close popups on outside click
  document.addEventListener('click', () => {
    sleepPopup.style.display = 'none';
    speedPopup.style.display = 'none';
  });

  // Keyboard shortcuts
  document.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT') return;
    if (e.code === 'Space') { e.preventDefault(); document.getElementById('btn-play-pause').click(); }
    if (e.code === 'ArrowLeft') audio.currentTime -= 5;
    if (e.code === 'ArrowRight') audio.currentTime += 5;
    if (e.code === 'ArrowUp') { audio.volume = Math.min(1, audio.volume + 0.1); volSlider.value = audio.volume; updateVolIcon(); }
    if (e.code === 'ArrowDown') { audio.volume = Math.max(0, audio.volume - 0.1); volSlider.value = audio.volume; updateVolIcon(); }
  });

  return { play };
})();

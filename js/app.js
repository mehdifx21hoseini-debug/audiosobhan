// ============================================================
// APP.JS — منطق اصلی اپلیکیشن
// ============================================================

// ---- Preloader ----
window.addEventListener('load', () => {
  setTimeout(() => {
    const preloader = document.getElementById('preloader');
    preloader.style.opacity = '0';
    setTimeout(() => { preloader.style.display = 'none'; }, 500);
  }, 1200);
});

// ---- Theme ----
const themeToggle = document.getElementById('theme-toggle');
const themeIcon = document.getElementById('theme-icon');

function applyTheme(t) {
  document.documentElement.setAttribute('data-theme', t);
  localStorage.setItem('ssa_theme', t);
  themeIcon.className = t === 'dark' ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
}

themeToggle.addEventListener('click', () => {
  const current = document.documentElement.getAttribute('data-theme');
  applyTheme(current === 'dark' ? 'light' : 'dark');
});

applyTheme(localStorage.getItem('ssa_theme') || 'dark');

// ---- Navigation ----
window.showPage = function(id) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById(id)?.classList.add('active');
  document.querySelectorAll('.nav-link').forEach(a => {
    a.classList.toggle('active', a.dataset.page === id);
  });
  window.scrollTo({ top: 0, behavior: 'smooth' });
  closeMobileMenu();
};

document.querySelectorAll('.nav-link').forEach(a => {
  a.addEventListener('click', (e) => {
    e.preventDefault();
    showPage(a.dataset.page);
  });
});

// ---- Mobile menu ----
const mobileBtn = document.getElementById('mobile-menu-btn');
const navLinks = document.getElementById('nav-links');

mobileBtn.addEventListener('click', () => {
  navLinks.classList.toggle('mobile-open');
});

function closeMobileMenu() {
  navLinks.classList.remove('mobile-open');
}

// ---- Sticky header ----
const header = document.getElementById('main-header');
window.addEventListener('scroll', () => {
  header.classList.toggle('scrolled', window.scrollY > 50);
});

// ---- Toast ----
window.showToast = function(msg, type = 'info') {
  const wrap = document.getElementById('toast-wrap');
  const t = document.createElement('div');
  t.className = `toast toast-${type}`;
  t.innerHTML = `<i class="fa-solid ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-circle-xmark' : 'fa-info-circle'}"></i><span>${msg}</span>`;
  wrap.appendChild(t);
  requestAnimationFrame(() => t.classList.add('toast-show'));
  setTimeout(() => {
    t.classList.remove('toast-show');
    setTimeout(() => t.remove(), 400);
  }, 3500);
};

// ---- Stars helper ----
function renderStars(rating) {
  let s = '';
  for (let i = 1; i <= 5; i++) {
    if (i <= Math.floor(rating)) s += '<i class="fa-solid fa-star"></i>';
    else if (i - rating < 1) s += '<i class="fa-solid fa-star-half-stroke"></i>';
    else s += '<i class="fa-regular fa-star"></i>';
  }
  return s;
}

function toPersian(n) {
  return n.toString().replace(/\d/g, d => '۰۱۲۳۴۵۶۷۸۹'[d]);
}

// ---- Book Card HTML ----
function bookCardHTML(book) {
  const catInfo = CATEGORIES[book.category] || {};
  return `
  <div class="book-card" data-id="${book.id}" data-cat="${book.category}">
    <div class="book-cover-wrap">
      <img src="${book.cover}" alt="${book.title}" class="book-cover" loading="lazy" />
      <div class="book-cover-overlay">
        <button class="play-btn-overlay" onclick="openBookModal(${book.id})">
          <i class="fa-solid fa-play"></i>
        </button>
      </div>
      <div class="book-cat-badge">${catInfo.label || ''}</div>
    </div>
    <div class="book-info">
      <h3 class="book-title">${book.title}</h3>
      <p class="book-author">${book.author}</p>
      <div class="book-meta">
        <div class="stars-row">${renderStars(book.rating)}<span>${toPersian(book.rating)}</span></div>
        <span class="book-duration"><i class="fa-regular fa-clock"></i> ${book.duration}</span>
      </div>
      <div class="book-actions">
        <button class="btn btn-gold btn-sm" onclick="Player.play(BOOKS.find(b=>b.id===${book.id}))">
          <i class="fa-solid fa-headphones"></i> گوش دادن
        </button>
        <button class="btn btn-outline btn-sm" onclick="openBookModal(${book.id})">
          <i class="fa-solid fa-info-circle"></i> جزئیات
        </button>
      </div>
    </div>
  </div>`;
}

// ---- Featured Swiper ----
function initFeaturedSwiper() {
  const wrapper = document.getElementById('featured-swiper-wrapper');
  const featured = BOOKS.filter(b => b.featured);
  wrapper.innerHTML = featured.map(b => `
    <div class="swiper-slide">
      <div class="featured-slide">
        <div class="fs-cover">
          <img src="${b.cover}" alt="${b.title}" loading="lazy" />
          <div class="fs-cover-glow"></div>
        </div>
        <div class="fs-content">
          <span class="fs-cat">${CATEGORIES[b.category]?.label}</span>
          <h2>${b.title}</h2>
          <p class="fs-original">${b.originalTitle}</p>
          <p class="fs-author"><i class="fa-solid fa-pen-nib"></i> ${b.author}</p>
          <p class="fs-desc">${b.description.substring(0, 120)}...</p>
          <div class="fs-meta">
            <div class="stars-row">${renderStars(b.rating)}<span>${toPersian(b.rating)} (${toPersian(b.reviews)} نظر)</span></div>
            <span><i class="fa-regular fa-clock"></i> ${b.duration}</span>
          </div>
          <div class="fs-actions">
            <button class="btn btn-gold" onclick="Player.play(BOOKS.find(x=>x.id===${b.id}))">
              <i class="fa-solid fa-play"></i> پخش
            </button>
            <button class="btn btn-outline" onclick="openBookModal(${b.id})">
              <i class="fa-solid fa-list"></i> فهرست فصل‌ها
            </button>
          </div>
        </div>
      </div>
    </div>
  `).join('');

  new Swiper('.featured-swiper', {
    slidesPerView: 1,
    spaceBetween: 30,
    loop: true,
    autoplay: { delay: 5000, disableOnInteraction: false },
    pagination: { el: '.swiper-pagination', clickable: true },
    navigation: { nextEl: '.swiper-button-next', prevEl: '.swiper-button-prev' },
    effect: 'fade',
    fadeEffect: { crossFade: true }
  });
}

// ---- Library Grid ----
let currentFilter = 'all';
let currentSort = 'default';

function renderLibrary() {
  const grid = document.getElementById('books-grid');
  let books = currentFilter === 'all' ? [...BOOKS] : BOOKS.filter(b => b.category === currentFilter);

  if (currentSort === 'name') books.sort((a, b) => a.title.localeCompare(b.title, 'fa'));
  if (currentSort === 'rating') books.sort((a, b) => b.rating - a.rating);
  if (currentSort === 'duration') books.sort((a, b) => b.durationSec - a.durationSec);

  grid.innerHTML = books.map(bookCardHTML).join('');
  animateCards();
}

function animateCards() {
  document.querySelectorAll('.book-card').forEach((c, i) => {
    c.style.animationDelay = `${i * 0.05}s`;
    c.classList.add('card-animate');
  });
}

// Filter tabs
document.getElementById('filter-tabs').addEventListener('click', (e) => {
  const btn = e.target.closest('.filter-tab');
  if (!btn) return;
  document.querySelectorAll('.filter-tab').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  currentFilter = btn.dataset.cat;
  renderLibrary();
});

document.getElementById('sort-select').addEventListener('change', (e) => {
  currentSort = e.target.value;
  renderLibrary();
});

// ---- Categories Full ----
function renderCategories() {
  const grid = document.getElementById('full-cats-grid');
  grid.innerHTML = Object.entries(CATEGORIES).map(([key, cat]) => {
    const catBooks = BOOKS.filter(b => b.category === key);
    return `
    <div class="full-cat-card" onclick="filterCategory('${key}')">
      <div class="fcat-header">
        <div class="fcat-icon"><i class="fa-solid ${cat.icon}"></i></div>
        <div>
          <h2>${cat.label}</h2>
          <p>${toPersian(catBooks.length)} کتاب صوتی</p>
        </div>
      </div>
      <p class="fcat-desc">${cat.desc}</p>
      <div class="fcat-books">
        ${catBooks.slice(0, 3).map(b => `
          <div class="fcat-book-item" onclick="event.stopPropagation(); openBookModal(${b.id})">
            <img src="${b.cover}" alt="${b.title}" />
            <span>${b.title}</span>
          </div>
        `).join('')}
      </div>
      <button class="btn btn-outline btn-sm">مشاهده همه <i class="fa-solid fa-arrow-left"></i></button>
    </div>`;
  }).join('');
}

window.filterCategory = function(cat) {
  showPage('library');
  setTimeout(() => {
    currentFilter = cat;
    document.querySelectorAll('.filter-tab').forEach(b => {
      b.classList.toggle('active', b.dataset.cat === cat);
    });
    renderLibrary();
  }, 100);
};

// ---- Book Modal ----
window.openBookModal = function(id) {
  const book = BOOKS.find(b => b.id === id);
  if (!book) return;
  const modal = document.getElementById('book-modal');
  const content = document.getElementById('modal-content');
  const catInfo = CATEGORIES[book.category] || {};

  content.innerHTML = `
    <div class="modal-book">
      <div class="modal-book-left">
        <img src="${book.cover}" alt="${book.title}" class="modal-cover" />
        <div class="modal-book-meta">
          <div class="stars-row">${renderStars(book.rating)}<span>${toPersian(book.rating)}</span></div>
          <p><i class="fa-solid fa-comments"></i> ${toPersian(book.reviews)} نظر</p>
          <p><i class="fa-regular fa-clock"></i> ${book.duration}</p>
          <p><i class="fa-solid fa-tag"></i> ${catInfo.label || ''}</p>
          <p><i class="fa-solid fa-translate"></i> ${book.translator}</p>
        </div>
        <button class="btn btn-gold btn-full" onclick="Player.play(BOOKS.find(b=>b.id===${book.id})); closeModal();">
          <i class="fa-solid fa-play"></i> شروع گوش دادن
        </button>
      </div>
      <div class="modal-book-right">
        <span class="modal-cat">${catInfo.label || ''}</span>
        <h2>${book.title}</h2>
        <p class="modal-original">${book.originalTitle}</p>
        <p class="modal-author"><i class="fa-solid fa-pen-nib"></i> ${book.author}</p>
        <div class="modal-tags">${(book.tags||[]).map(t=>`<span class="tag">${t}</span>`).join('')}</div>
        <p class="modal-desc">${book.description}</p>
        <h3 class="chapters-title"><i class="fa-solid fa-list-ol"></i> فهرست فصل‌ها</h3>
        <ul class="chapters-list">
          ${book.chapters.map((ch, i) => `
            <li class="chapter-item" onclick="Player.play(BOOKS.find(b=>b.id===${book.id}), ${i}); closeModal();">
              <div class="chapter-num">${toPersian(i + 1)}</div>
              <div class="chapter-info">
                <span class="chapter-name">${ch.title}</span>
                <span class="chapter-dur">${ch.duration}</span>
              </div>
              <button class="chapter-play-btn"><i class="fa-solid fa-play"></i></button>
            </li>
          `).join('')}
        </ul>
      </div>
    </div>`;

  modal.style.display = 'flex';
  requestAnimationFrame(() => modal.classList.add('modal-open'));
};

window.closeModal = function() {
  const modal = document.getElementById('book-modal');
  modal.classList.remove('modal-open');
  setTimeout(() => { modal.style.display = 'none'; }, 350);
};

document.getElementById('modal-close').addEventListener('click', closeModal);
document.getElementById('book-modal').addEventListener('click', (e) => {
  if (e.target === e.currentTarget) closeModal();
});

// ---- Search ----
const searchBtn = document.getElementById('search-btn');
const searchOverlay = document.getElementById('search-overlay');
const searchClose = document.getElementById('search-close');
const searchInput = document.getElementById('search-input');
const searchResults = document.getElementById('search-results');

searchBtn.addEventListener('click', () => {
  searchOverlay.classList.add('search-open');
  setTimeout(() => searchInput.focus(), 300);
});

searchClose.addEventListener('click', () => {
  searchOverlay.classList.remove('search-open');
});

searchInput.addEventListener('input', () => {
  const q = searchInput.value.trim().toLowerCase();
  if (!q) { searchResults.innerHTML = ''; return; }
  const results = BOOKS.filter(b =>
    b.title.includes(q) || b.author.toLowerCase().includes(q) ||
    b.originalTitle.toLowerCase().includes(q) || (b.tags || []).some(t => t.includes(q))
  );
  if (results.length === 0) {
    searchResults.innerHTML = '<p class="no-results">نتیجه‌ای یافت نشد</p>';
    return;
  }
  searchResults.innerHTML = results.map(b => `
    <div class="search-result-item" onclick="openBookModal(${b.id}); searchOverlay.classList.remove('search-open')">
      <img src="${b.cover}" alt="${b.title}" />
      <div>
        <strong>${b.title}</strong>
        <span>${b.author}</span>
      </div>
      <div class="stars-row mini">${renderStars(b.rating)}</div>
    </div>
  `).join('');
});

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    searchOverlay.classList.remove('search-open');
    closeModal();
  }
});

// ---- Particles ----
(function initParticles() {
  const canvas = document.getElementById('particles-canvas');
  const ctx = canvas.getContext('2d');
  let W, H, particles = [];

  function resize() {
    W = canvas.width = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }
  resize();
  window.addEventListener('resize', resize);

  for (let i = 0; i < 50; i++) {
    particles.push({
      x: Math.random() * W, y: Math.random() * H,
      r: Math.random() * 1.5 + 0.5,
      vx: (Math.random() - 0.5) * 0.3,
      vy: (Math.random() - 0.5) * 0.3,
      o: Math.random() * 0.4 + 0.1
    });
  }

  function draw() {
    ctx.clearRect(0, 0, W, H);
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    particles.forEach(p => {
      p.x += p.vx; p.y += p.vy;
      if (p.x < 0) p.x = W; if (p.x > W) p.x = 0;
      if (p.y < 0) p.y = H; if (p.y > H) p.y = 0;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = isDark ? `rgba(184,134,11,${p.o})` : `rgba(30,58,95,${p.o})`;
      ctx.fill();
    });
    requestAnimationFrame(draw);
  }
  draw();
})();

// ---- Init ----
document.addEventListener('DOMContentLoaded', () => {
  // Update book count
  document.getElementById('book-count').textContent = toPersian(BOOKS.length);

  initFeaturedSwiper();
  renderLibrary();
  renderCategories();
});

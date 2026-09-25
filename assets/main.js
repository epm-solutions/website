const nav = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  nav.classList.toggle('scrolled', window.scrollY > 50);
});

const toggle = document.getElementById('navToggle');
const links = document.getElementById('navLinks');
toggle.addEventListener('click', () => {
  links.classList.toggle('open');
});
links.querySelectorAll('a').forEach(a => {
  a.addEventListener('click', () => links.classList.remove('open'));
});

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry, i) => {
    if (entry.isIntersecting) {
      entry.target.style.transitionDelay = (i * 0.05) + 's';
      entry.target.classList.add('visible');
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

const lightbox = document.getElementById('lightbox');
if (lightbox) {
  const lbImg = document.getElementById('lightboxImg');
  const lbCap = document.getElementById('lightboxCaption');
  const btnClose = lightbox.querySelector('.lightbox-close');
  const btnPrev = lightbox.querySelector('.lightbox-prev');
  const btnNext = lightbox.querySelector('.lightbox-next');
  let currentList = [];
  let currentIndex = 0;

  function render() {
    const item = currentList[currentIndex];
    lbImg.src = item.src;
    lbImg.alt = item.caption || '';
    lbCap.textContent = item.caption || '';
    const multi = currentList.length > 1;
    btnPrev.style.display = multi ? '' : 'none';
    btnNext.style.display = multi ? '' : 'none';
  }
  function open(list, index) {
    currentList = list;
    currentIndex = index;
    render();
    lightbox.hidden = false;
    requestAnimationFrame(() => lightbox.classList.add('open'));
    document.body.style.overflow = 'hidden';
  }
  function close() {
    lightbox.classList.remove('open');
    document.body.style.overflow = '';
    setTimeout(() => { lightbox.hidden = true; }, 250);
  }
  function next() {
    currentIndex = (currentIndex + 1) % currentList.length;
    render();
  }
  function prev() {
    currentIndex = (currentIndex - 1 + currentList.length) % currentList.length;
    render();
  }

  document.querySelectorAll('.project-carousel').forEach(carousel => {
    const photos = Array.from(carousel.querySelectorAll('.carousel-photo'));
    const list = photos.map(a => ({
      src: a.getAttribute('href'),
      caption: a.dataset.caption || ''
    }));
    photos.forEach((a, i) => {
      a.addEventListener('click', e => {
        e.preventDefault();
        open(list, i);
      });
    });
  });

  btnClose.addEventListener('click', close);
  btnPrev.addEventListener('click', prev);
  btnNext.addEventListener('click', next);
  lightbox.addEventListener('click', e => {
    if (e.target === lightbox) close();
  });
  document.addEventListener('keydown', e => {
    if (lightbox.hidden) return;
    if (e.key === 'Escape') close();
    if (e.key === 'ArrowRight') next();
    if (e.key === 'ArrowLeft') prev();
  });
}

document.querySelectorAll('.project-carousel').forEach(carousel => {
  const slides = Array.from(carousel.querySelectorAll('.carousel-slide'));
  if (!slides.length) return;
  const dotsContainer = carousel.querySelector('.carousel-dots');
  const prevBtn = carousel.querySelector('.carousel-prev');
  const nextBtn = carousel.querySelector('.carousel-next');
  const progressBar = carousel.querySelector('.carousel-progress > span');
  const interval = parseInt(carousel.dataset.interval, 10) || 5000;
  let current = slides.findIndex(s => s.classList.contains('is-active'));
  if (current < 0) current = 0;
  let paused = false;
  let startTime = performance.now();
  let rafId = null;

  const dots = slides.map((_, i) => {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'carousel-dot' + (i === current ? ' is-active' : '');
    b.setAttribute('role', 'tab');
    b.setAttribute('aria-label', 'Diapositiva ' + (i + 1));
    b.addEventListener('click', () => goTo(i, true));
    dotsContainer && dotsContainer.appendChild(b);
    return b;
  });

  function activate(i) {
    slides[current].classList.remove('is-active');
    slides[current].setAttribute('aria-hidden', 'true');
    dots[current] && dots[current].classList.remove('is-active');
    current = (i + slides.length) % slides.length;
    slides[current].classList.add('is-active');
    slides[current].setAttribute('aria-hidden', 'false');
    dots[current] && dots[current].classList.add('is-active');
  }
  function goTo(i, resetTimer) {
    activate(i);
    if (resetTimer) startTime = performance.now();
  }
  function tick(now) {
    if (!paused) {
      const elapsed = now - startTime;
      const pct = Math.min(elapsed / interval, 1);
      if (progressBar) progressBar.style.width = (pct * 100) + '%';
      if (pct >= 1) {
        activate(current + 1);
        startTime = now;
        if (progressBar) progressBar.style.width = '0%';
      }
    } else {
      startTime = now - (progressBar ? (parseFloat(progressBar.style.width) || 0) * interval / 100 : 0);
    }
    rafId = requestAnimationFrame(tick);
  }

  prevBtn && prevBtn.addEventListener('click', () => goTo(current - 1, true));
  nextBtn && nextBtn.addEventListener('click', () => goTo(current + 1, true));
  carousel.addEventListener('mouseenter', () => { paused = true; carousel.classList.add('is-paused'); });
  carousel.addEventListener('mouseleave', () => { paused = false; carousel.classList.remove('is-paused'); });
  carousel.addEventListener('focusin', () => { paused = true; carousel.classList.add('is-paused'); });
  carousel.addEventListener('focusout', (e) => {
    if (!carousel.contains(e.relatedTarget)) {
      paused = false;
      carousel.classList.remove('is-paused');
    }
  });

  // Autoplay solo cuando el carrusel es visible
  const io = new IntersectionObserver(([entry]) => {
    if (entry.isIntersecting) {
      if (rafId == null) {
        startTime = performance.now();
        rafId = requestAnimationFrame(tick);
      }
    } else if (rafId != null) {
      cancelAnimationFrame(rafId);
      rafId = null;
      if (progressBar) progressBar.style.width = '0%';
    }
  }, { threshold: 0.25 });
  io.observe(carousel);
});

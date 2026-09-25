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

  document.querySelectorAll('.project-gallery').forEach(gallery => {
    const photos = Array.from(gallery.querySelectorAll('.project-photo'));
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

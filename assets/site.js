// Public R2 video previews load only when near the viewport.
const previews = [...document.querySelectorAll('video.motion-preview[data-preview]')];
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
if (!reducedMotion.matches && 'IntersectionObserver' in window) {
  const observer = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      const video = entry.target;
      if (entry.isIntersecting && !document.hidden) {
        if (!video.src) video.src = video.dataset.preview;
        video.play().catch(() => {});
      } else video.pause();
    }
  }, { threshold: 0.18, rootMargin: '100px 0px' });
  previews.forEach((video) => observer.observe(video));
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) previews.forEach((video) => video.pause());
  });
}

// Homepage hero: one title from every published R2 film per round; 20 of 32
// picks are science, mechanism, brand, manufacturing, or technical content.
const playlistNode = document.querySelector('#hero-playlist');
if (playlistNode) {
  const playlist = JSON.parse(playlistNode.textContent);
  const hero = document.querySelector('.hero-cinema');
  const video = hero.querySelector('.hero-reel');
  const fallback = hero.querySelector('.hero-fallback');
  const title = hero.querySelector('#hero-title');
  const category = hero.querySelector('#hero-category');
    const points = hero.querySelector('#hero-points');
  const watch = hero.querySelector('#hero-watch');
  const counter = hero.querySelector('#hero-index');
  const sound = hero.querySelector('#hero-sound');
  const motion = hero.querySelector('#hero-motion');
  const priority = playlist.filter((item) => item.priority);
  const product = playlist.filter((item) => !item.priority);
  const priorityRatio = priority.length / playlist.length;
  if (playlist.length !== 32 || priorityRatio <= 0.5) throw new Error('Hero carousel needs all films and a priority share above 50%.');

  const shuffle = (items) => {
    const copy = [...items];
    for (let i = copy.length - 1; i > 0; i -= 1) {
      const j = Math.floor(Math.random() * (i + 1));
      [copy[i], copy[j]] = [copy[j], copy[i]];
    }
    return copy;
  };
  const newRound = () => {
    const high = shuffle(priority);
    const low = shuffle(product);
    const round = [];
    for (let i = 0; i < playlist.length; i += 1) {
      const needsHigh = Math.floor(((i + 1) * priority.length) / playlist.length) > Math.floor((i * priority.length) / playlist.length);
      round.push(needsHigh ? high.shift() : low.shift());
    }
    return round;
  };

  let round = newRound();
  let position = 0;
  let timer = 0;
  let soundEnabled = false;
  let motionPaused = false;
  const dwellMs = 10000;

  const setSoundState = (enabled) => {
    soundEnabled = enabled;
    sound.setAttribute('aria-pressed', String(enabled));
    sound.textContent = enabled ? '關閉聲音' : '播放旁白';
    video.muted = !enabled;
  };
  const scheduleAdvance = () => {
    window.clearTimeout(timer);
    if (document.hidden || reducedMotion.matches || soundEnabled || motionPaused) return;
    timer = window.setTimeout(() => move(1), dwellMs);
  };
  const show = () => {
    const item = round[position];
    window.clearTimeout(timer);
    video.classList.remove('is-playing');
    video.pause();
    video.removeAttribute('src');
    video.load();
    fallback.style.cssText = item.poster;
    title.textContent = item.title;
    category.textContent = item.category;
    points.replaceChildren(...item.points.map((point) => {
      const li = document.createElement('li');
      li.textContent = point;
      return li;
    }));
    watch.href = item.watch;
    watch.textContent = `觀看完整影片 ↗`;
    counter.textContent = `${String(position + 1).padStart(2, '0')} / ${playlist.length}`;
    setSoundState(false);
    video.src = item.src;
    video.load();
    if (!reducedMotion.matches && !document.hidden && !motionPaused) video.play().catch(() => {});
    scheduleAdvance();
  };
  video.addEventListener('playing', () => {
    if (video.readyState >= HTMLMediaElement.HAVE_CURRENT_DATA && video.currentSrc === round[position].src) {
      video.classList.add('is-playing');
    }
  });
  for (const eventName of ['error', 'stalled', 'waiting', 'emptied']) {
    video.addEventListener(eventName, () => video.classList.remove('is-playing'));
  }
  const move = (step) => {
    position += step;
    if (position >= round.length) {
      round = newRound();
      position = 0;
    } else if (position < 0) {
      round = newRound();
      position = round.length - 1;
    }
    show();
  };

  hero.querySelector('#hero-prev').addEventListener('click', () => move(-1));
  hero.querySelector('#hero-next').addEventListener('click', () => move(1));
  motion.addEventListener('click', () => {
    motionPaused = !motionPaused;
    motion.textContent = motionPaused ? '繼續' : '暫停';
    motion.setAttribute('aria-label', motionPaused ? '繼續影片輪播' : '暫停影片輪播');
    if (motionPaused) {
      window.clearTimeout(timer);
      video.pause();
    } else {
      if (!reducedMotion.matches && !document.hidden) video.play().catch(() => {});
      scheduleAdvance();
    }
  });
  sound.addEventListener('click', () => {
    if (!soundEnabled) {
      window.clearTimeout(timer);
      setSoundState(true);
      const startAudio = () => {
        try { video.currentTime = 0; } catch {}
        if (!motionPaused) video.play().catch(() => setSoundState(false));
      };
      if (video.readyState >= 1) startAudio();
      else video.addEventListener('loadedmetadata', startAudio, { once: true });
    } else {
      setSoundState(false);
      video.currentTime = 0;
      video.play().catch(() => {});
      scheduleAdvance();
    }
  });
  video.addEventListener('ended', () => {
    if (soundEnabled) move(1);
  });
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      window.clearTimeout(timer);
      video.pause();
    } else {
      if (!reducedMotion.matches && !motionPaused) video.play().catch(() => {});
      scheduleAdvance();
    }
  });
  show();
}

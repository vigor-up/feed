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

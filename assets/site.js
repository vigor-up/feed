// Load short public R2 previews only when they can be seen.
const previews = [...document.querySelectorAll('video.motion-preview[data-preview]')];
if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches && 'IntersectionObserver' in window) {
  const observer = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      const video = entry.target;
      if (entry.isIntersecting && !document.hidden) {
        if (!video.src) video.src = video.dataset.preview;
        video.play().catch(() => {});
      } else {
        video.pause();
      }
    }
  }, { threshold: 0.25, rootMargin: '80px 0px' });
  previews.forEach((video) => observer.observe(video));
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) previews.forEach((video) => video.pause());
    else previews.filter((video) => video.src && video.getBoundingClientRect().top < innerHeight && video.getBoundingClientRect().bottom > 0)
      .forEach((video) => video.play().catch(() => {}));
  });
}

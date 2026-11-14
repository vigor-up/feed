// Short public R2 previews load only while their cards are near the viewport.
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

// All ROI inputs remain in this browser. No preset performance values are used.
document.querySelectorAll('.roi-calc').forEach((form) => {
  const result = form.querySelector('output');
  const read = (name) => Number(form.elements[name].value || 0);
  const update = () => {
    const investment = read('investment');
    const extra = read('extra');
    const price = read('price');
    const feed = read('feed');
    const feedPrice = read('feed_price');
    if (investment <= 0 || (extra <= 0 && feed <= 0)) {
      result.textContent = '—%';
      return;
    }
    const net = extra * price + feed * feedPrice - investment;
    const roi = net / investment * 100;
    result.textContent = `${new Intl.NumberFormat('zh-CN', { maximumFractionDigits: 1 }).format(roi)}%`;
  };
  form.addEventListener('input', update);
  form.addEventListener('change', update);
  form.addEventListener('submit', (event) => event.preventDefault());
});

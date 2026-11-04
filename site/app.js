const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

const revealItems = document.querySelectorAll('.reveal');
if (reduced) {
  revealItems.forEach((item) => item.classList.add('is-visible'));
} else if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        obs.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });
  revealItems.forEach((item) => observer.observe(item));
} else {
  revealItems.forEach((item) => item.classList.add('is-visible'));
}

document.querySelectorAll('[data-count]').forEach((node) => {
  const end = Number(node.dataset.count);
  if (reduced || !('IntersectionObserver' in window)) {
    node.textContent = end;
    return;
  }
  const countObserver = new IntersectionObserver((entries, obs) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      let current = 0;
      const step = Math.max(1, Math.ceil(end / 28));
      const timer = window.setInterval(() => {
        current = Math.min(end, current + step);
        node.textContent = current;
        if (current >= end) window.clearInterval(timer);
      }, 35);
      obs.unobserve(node);
    });
  }, { threshold: 1 });
  countObserver.observe(node);
});

// Keep external navigation intentional while preserving ordinary HTML links.
document.querySelectorAll('a[href]').forEach((link) => {
  link.addEventListener('click', () => link.classList.add('is-clicked'));
});

(() => {
  const gate = document.querySelector('[data-age-gate]');
  if (!gate) return;
  const key = 'museai-age-confirmed';
  const params = new URLSearchParams(window.location.search);
  const confirmed = window.localStorage.getItem(key) === 'yes' || params.get('age') === 'confirmed';
  const content = document.querySelector('#donation-content');

  const setState = (allowed) => {
    gate.hidden = allowed;
    document.body.classList.toggle('age-locked', !allowed);
    if (content) content.setAttribute('aria-hidden', String(!allowed));
  };

  if (confirmed) {
    window.localStorage.setItem(key, 'yes');
    setState(true);
  } else {
    setState(false);
  }

  const confirm = gate.querySelector('[data-age-confirm]');
  confirm?.addEventListener('click', () => {
    window.localStorage.setItem(key, 'yes');
    setState(true);
  });
})();

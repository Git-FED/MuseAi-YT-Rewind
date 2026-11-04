(() => {
  const nsfwButton = document.getElementById('nsfwBtn');
  const gate = document.getElementById('ageGate');
  const emailRequest = document.getElementById('emailRequest');
  const checkbox = document.getElementById('ageCheck');
  const confirm = document.getElementById('ageConfirm');
  const cancel = document.getElementById('ageCancel');
  const closeEmail = document.getElementById('emailClose');
  if (!nsfwButton || !gate || !emailRequest) return;

  nsfwButton.addEventListener('click', (event) => {
    event.preventDefault();
    checkbox.checked = false;
    confirm.disabled = true;
    gate.showModal();
  });

  checkbox.addEventListener('change', () => { confirm.disabled = !checkbox.checked; });
  confirm.addEventListener('click', () => {
    if (!checkbox.checked) return;
    gate.close();
    emailRequest.showModal();
  });
  cancel.addEventListener('click', () => gate.close());
  closeEmail.addEventListener('click', () => emailRequest.close());
  gate.addEventListener('click', (event) => { if (event.target === gate) gate.close(); });
  emailRequest.addEventListener('click', (event) => { if (event.target === emailRequest) emailRequest.close(); });
})();

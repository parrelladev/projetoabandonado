(function () {
  const form = document.querySelector('.search-box');
  if (!form) return;
  const input = form.querySelector('input');
  const cards = Array.from(document.querySelectorAll('.post-card'));
  const empty = document.getElementById('no-results');
  const status = document.getElementById('search-status');
  form.addEventListener('submit', (event) => event.preventDefault());
  input.addEventListener('input', () => {
    const query = input.value.trim().toLocaleLowerCase('pt-BR');
    let shown = 0;
    cards.forEach((card) => {
      const match = !query || (card.dataset.search || '').includes(query);
      card.hidden = !match;
      if (match) shown += 1;
    });
    empty.hidden = shown > 0;
    status.textContent = query ? `${shown} ${shown === 1 ? 'resultado' : 'resultados'}` : '';
  });
}());

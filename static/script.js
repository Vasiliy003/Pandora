// Универсальные функции для работы с модалками
function openModal(id = 'modal') {
  const modal = document.getElementById(id);
  if (!modal) return;
  modal.style.display = 'flex';
  // Ставим фокус на инпут с id "flagInput", если он есть внутри модалки
  setTimeout(() => {
    const flagInput = modal.querySelector('#flagInput') || document.getElementById('flagInput');
    if (flagInput) flagInput.focus();
  }, 200);
}

function closeModal(id = 'modal') {
  const modal = document.getElementById(id);
  if (modal) modal.style.display = 'none';
}

// Обратная совместимость: старые имена оставляем как обёртки
function openCssModal() { openModal('modal'); }
function closeCssModal() { closeModal('modal'); }
function openXssModal() { openModal('xss-modal'); }
function closeXssModal() { closeModal('xss-modal'); }

window.openModal = openModal;
window.closeModal = closeModal;
window.openCssModal = openCssModal;
window.closeCssModal = closeCssModal;
window.openXssModal = openXssModal;
window.closeXssModal = closeXssModal;

// Клик по карточкам открывает соответствующие модалки
document.querySelectorAll('.css-card').forEach(card => {
  card.addEventListener('click', () => openModal('modal'));
});
document.querySelectorAll('.xss-card').forEach(card => {
  card.addEventListener('click', () => openModal('xss-modal'));
});

// Умное закрытие по Escape: скрываем все видимые модалки
document.addEventListener('keydown', function (e) {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal').forEach(modal => {
      const style = window.getComputedStyle(modal);
      if (style && style.display !== 'none') modal.style.display = 'none';
    });
  }
});

// Примечание: закрытие по клику вне модалки явно отключено по дизайну — по требованию пользователя.

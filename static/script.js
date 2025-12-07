function openCssModal() {
  const modal = document.getElementById("modal");
  if (modal) {
    modal.style.display = "flex";
    setTimeout(() => {
      const flagInput = document.getElementById("flagInput");
      if (flagInput) flagInput.focus();
    }, 200);
  }
}

function closeCssModal() {
  const modal = document.getElementById("modal");
  if (modal) modal.style.display = "none";
}

// Открытие модального окна по клику на любую карточку
document.querySelectorAll('.css-card').forEach(card => {
  card.addEventListener('click', openCssModal);
});

// Закрытие при клике вне контента
document.addEventListener("click", function (e) {
  const modal = document.getElementById("modal");
  if (!modal) return;
  if (modal.style.display !== "flex") return;
  const content = modal.querySelector(".modal-content");
  if (!content) return;
  if (!content.contains(e.target) && !e.target.classList.contains("card")) {
    closeCssModal();
  }
});

// Закрытие по Escape
document.addEventListener("keydown", function (e) {
  if (e.key === "Escape") closeCssModal();
});

window.openCssModal = openCssModal;
window.closeCssModal = closeCssModal;

// Для xss

function openXssModal() {
  const modal = document.getElementById("xss-modal");
  if (modal) {
    modal.style.display = "flex";
    setTimeout(() => {
      const flagInput = document.getElementById("flagInput");
      if (flagInput) flagInput.focus();
    }, 200);
  }
}

function closeXssModal() {
  const modal = document.getElementById("xss-modal");
  if (modal) modal.style.display = "none";
}

// Открытие модального окна по клику на любую карточку
document.querySelectorAll('.xss-card').forEach(card => {
  card.addEventListener('click', openXssModal);
});

// Закрытие при клике вне контента
document.addEventListener("click", function (e) {
  const modal = document.getElementById("xss-modal");
  if (!modal) return;
  if (modal.style.display !== "flex") return;
  const content = modal.querySelector(".modal-content");
  if (!content) return;
  if (!content.contains(e.target) && !e.target.classList.contains("card")) {
    closeXssModal();
  }
});

// Закрытие по Escape
document.addEventListener("keydown", function (e) {
  if (e.key === "Escape") closeXssModal();
});

window.openXssModal = openXssModal;
window.closeXssModal = closeXssModal;
function openModal() {
  const modal = document.getElementById("modal");
  if (modal) {
    modal.style.display = "flex";
    setTimeout(() => {
      const flagInput = document.getElementById("flagInput");
      if (flagInput) flagInput.focus();
    }, 200);
  }
}

function closeModal() {
  const modal = document.getElementById("modal");
  if (modal) modal.style.display = "none";
}

// Открытие модального окна по клику на любую карточку
document.querySelectorAll('.card').forEach(card => {
  card.addEventListener('click', openModal);
});

// Закрытие при клике вне контента
document.addEventListener("click", function (e) {
  const modal = document.getElementById("modal");
  if (!modal) return;
  if (modal.style.display !== "flex") return;
  const content = modal.querySelector(".modal-content");
  if (!content) return;
  if (!content.contains(e.target) && !e.target.classList.contains("card")) {
    closeModal();
  }
});

// Закрытие по Escape
document.addEventListener("keydown", function (e) {
  if (e.key === "Escape") closeModal();
});

window.openModal = openModal;
window.closeModal = closeModal;
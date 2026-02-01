let currentSlide = 0;

function openHelpModal(e) {
  if (e && e.stopPropagation) e.stopPropagation();
  const other = document.getElementById('helpModalXss');
  if (other) other.style.display = 'none';

  const taskModal = document.getElementById('modal');
  if (taskModal) {
    const style = window.getComputedStyle(taskModal);
    if (style && style.display !== 'none') taskModal.style.display = 'none';
  }

  const el = document.getElementById("helpModal");
  if (el) {
    el.style.display = "flex";
    el.style.zIndex = 3000;
  }
  showSlide(0);
}

function closeHelpModal() {
  const el = document.getElementById("helpModal");
  if (el) el.style.display = "none";
  const taskModal = document.getElementById('modal');
  if (taskModal) taskModal.style.display = 'flex';
} 

function showSlide(index) {
  const slides = document.querySelectorAll(".help-slide");
  slides.forEach(s => s.classList.remove("active"));
  slides[index].classList.add("active");

  document.getElementById("slideIndicator").textContent =
    `${index + 1} / ${slides.length}`;

  currentSlide = index;
}

function nextSlide() {
  const slides = document.querySelectorAll(".help-slide");
  if (currentSlide < slides.length - 1) showSlide(currentSlide + 1);
}

function prevSlide() {
  if (currentSlide > 0) showSlide(currentSlide - 1);
}

/* XSS */
let currentSlideXss = 0;

function openHelpModalXss(e) {
  if (e && e.stopPropagation) e.stopPropagation();
  const other = document.getElementById('helpModal');
  if (other) other.style.display = 'none';

  const taskModal = document.getElementById('xss-modal');
  if (taskModal) {
    const style = window.getComputedStyle(taskModal);
    if (style && style.display !== 'none') taskModal.style.display = 'none';
  }

  const el = document.getElementById("helpModalXss");
  if (!el) return;

  if (el.parentElement !== document.body) document.body.appendChild(el);
  el.style.display = 'flex';
  el.style.zIndex = 3000;

  showXssSlide(0);
} 

function closeHelpModalXss() {
  const el = document.getElementById("helpModalXss");
  if (el) el.style.display = 'none';
  const taskModal = document.getElementById('xss-modal');
  if (taskModal) taskModal.style.display = 'flex';
}

function showXssSlide(index) {
  const slides = document.querySelectorAll("#helpModalXss .help-slide-xss");
  if (!slides || slides.length === 0) return;
  slides.forEach(s => s.classList.remove("active"));
  if (!slides[index]) return;
  slides[index].classList.add("active");

  const indicator = document.getElementById("slideIndicatorXss");
  if (indicator) indicator.textContent = `${index + 1} / ${slides.length}`;
  currentSlideXss = index;
} 

function nextXssSlide() {
  const slides = document.querySelectorAll("#helpModalXss .help-slide-xss");
  if (currentSlideXss < slides.length - 1) showXssSlide(currentSlideXss + 1);
}

function prevXssSlide() {
  if (currentSlideXss > 0) showXssSlide(currentSlideXss - 1);
}

document.addEventListener('DOMContentLoaded', function() {
  const btnXss = document.querySelector('#xss-modal .card-help-btn');
  if (btnXss) btnXss.addEventListener('click', function(e) { e.stopPropagation(); openHelpModalXss(e); });
  const btnSql = document.querySelector('#modal .card-help-btn');
  if (btnSql) btnSql.addEventListener('click', function(e) { e.stopPropagation(); openHelpModal(e); });
});

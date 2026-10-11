// TCAS Prep Application Client Logic

// 1. Toast Notification Helper
function showToast(message) {
  let toast = document.getElementById('toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'toast';
    document.body.appendChild(toast);
  }
  toast.innerText = message;
  toast.style.display = 'block';
  setTimeout(() => {
    toast.style.display = 'none';
  }, 3000);
}

// 2. One-click Copy to Clipboard
function copyToClipboard(text, successMsg = "คัดลอกลงคลิปบอร์ดแล้ว!") {
  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard.writeText(text).then(() => {
      showToast(successMsg);
    }).catch(err => {
      fallbackCopy(text, successMsg);
    });
  } else {
    fallbackCopy(text, successMsg);
  }
}

function fallbackCopy(text, successMsg) {
  const textArea = document.createElement("textarea");
  textArea.value = text;
  textArea.style.position = "fixed";
  textArea.style.left = "-999999px";
  document.body.appendChild(textArea);
  textArea.focus();
  textArea.select();
  try {
    document.execCommand('copy');
    showToast(successMsg);
  } catch (err) {
    showToast("ไม่สามารถคัดลอกได้โดยอัตโนมัติ");
  }
  document.body.removeChild(textArea);
}

// 3. Accordion Handler
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.accordion-header').forEach(header => {
    header.addEventListener('click', () => {
      const parent = header.closest('.accordion');
      parent.classList.toggle('open');
      const arrow = header.querySelector('.accordion-arrow');
      if (arrow) {
        arrow.textContent = parent.classList.contains('open') ? '▲' : '▼';
      }
    });
  });

  // Render KaTeX if available
  renderMathInDocument();
});

function renderMathInDocument() {
  if (window.renderMathInElement) {
    renderMathInElement(document.body, {
      delimiters: [
        {left: '$$', right: '$$', display: true},
        {left: '$', right: '$', display: false},
        {left: '\\[', right: '\\]', display: true},
        {left: '\\(', right: '\\)', display: false}
      ],
      throwOnError: false
    });
  }
}

// 4. Timer Logic
class PracticeTimer {
  constructor(displayElementId) {
    this.displayEl = document.getElementById(displayElementId);
    this.seconds = 0;
    this.interval = null;
    this.isRunning = false;
  }

  start() {
    if (this.isRunning) return;
    this.isRunning = true;
    this.interval = setInterval(() => {
      this.seconds++;
      this.updateDisplay();
    }, 1000);
  }

  stop() {
    this.isRunning = false;
    if (this.interval) clearInterval(this.interval);
    return this.seconds;
  }

  updateDisplay() {
    if (!this.displayEl) return;
    const mins = Math.floor(this.seconds / 60);
    const secs = this.seconds % 60;
    this.displayEl.textContent = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  }
}

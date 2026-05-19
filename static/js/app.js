// =====================
// GradeAI — app.js
// =====================

let extracurricularValue = 0;

function setToggle(btn, fieldId) {
  const group = btn.closest('.toggle-group');
  group.querySelectorAll('.toggle-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById(fieldId).value = btn.dataset.value;
  extracurricularValue = parseInt(btn.dataset.value);
}

document.getElementById('predictForm').addEventListener('submit', async function (e) {
  e.preventDefault();
  await runPrediction();
});

async function runPrediction() {
  const btn = document.getElementById('predictBtn');
  const btnText = btn.querySelector('.btn-text');
  const btnLoader = btn.querySelector('.btn-loader');
  const btnArrow = btn.querySelector('.btn-arrow');

  // Gather inputs
  const fields = {
    attendance:      document.getElementById('attendance'),
    assignment_avg:  document.getElementById('assignment_avg'),
    midterm_score:   document.getElementById('midterm_score'),
    hours_studied:   document.getElementById('hours_studied'),
    prev_gpa:        document.getElementById('prev_gpa'),
    sleep_hours:     document.getElementById('sleep_hours'),
  };

  // Clear errors
  Object.values(fields).forEach(f => f.classList.remove('error'));

  // Validate
  let valid = true;
  for (const [key, input] of Object.entries(fields)) {
    if (!input.value || input.value === '') {
      input.classList.add('error');
      valid = false;
    }
  }
  if (!valid) {
    shakeForm();
    return;
  }

  const payload = {
    attendance:      parseFloat(fields.attendance.value),
    assignment_avg:  parseFloat(fields.assignment_avg.value),
    midterm_score:   parseFloat(fields.midterm_score.value),
    hours_studied:   parseFloat(fields.hours_studied.value),
    prev_gpa:        parseFloat(fields.prev_gpa.value),
    sleep_hours:     parseFloat(fields.sleep_hours.value),
    extracurricular: extracurricularValue
  };

  // Loading state
  btn.disabled = true;
  btnText.style.display = 'none';
  btnArrow.style.display = 'none';
  btnLoader.style.display = 'flex';

  try {
    const response = await fetch('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await response.json();

    if (data.error) {
      showError(data.error);
      return;
    }

    renderResult(data);

  } catch (err) {
    showError('Could not connect to server. Make sure the Flask backend is running.');
  } finally {
    btn.disabled = false;
    btnText.style.display = 'inline';
    btnArrow.style.display = 'inline';
    btnLoader.style.display = 'none';
  }
}

function renderResult(data) {
  document.getElementById('emptyResult').style.display = 'none';
  const card = document.getElementById('resultCard');
  card.style.display = 'block';

  // Grade and emoji
  document.getElementById('resultEmoji').textContent = data.emoji;
  document.getElementById('resultGrade').textContent = data.prediction;
  document.getElementById('resultGrade').style.color = data.color;
  document.getElementById('confidenceValue').textContent = data.confidence + '%';
  document.getElementById('resultAdvice').textContent = data.advice;

  // Probability bars
  const probBars = document.getElementById('probBars');
  probBars.innerHTML = '';
  data.probabilities.forEach(p => {
    const row = document.createElement('div');
    row.className = 'prob-bar-row';
    row.innerHTML = `
      <div class="prob-label">${p.label}</div>
      <div class="prob-track">
        <div class="prob-fill" style="background:${p.color}" data-width="${p.probability}"></div>
      </div>
      <div class="prob-pct">${p.probability}%</div>
    `;
    probBars.appendChild(row);
  });

  // Animate bars after paint
  requestAnimationFrame(() => {
    setTimeout(() => {
      document.querySelectorAll('.prob-fill').forEach(bar => {
        bar.style.width = bar.dataset.width + '%';
      });
    }, 50);
  });

  // Factors
  const factorsSection = document.getElementById('factorsSection');
  const factorsList = document.getElementById('factorsList');
  factorsList.innerHTML = '';

  if (data.factors && data.factors.length > 0) {
    factorsSection.style.display = 'block';
    data.factors.forEach(f => {
      const item = document.createElement('div');
      item.className = 'factor-item';
      item.innerHTML = `
        <div class="factor-dot ${f.impact}"></div>
        <div class="factor-text">
          <div class="factor-label">${f.label}</div>
          <div class="factor-tip">${f.tip}</div>
        </div>
      `;
      factorsList.appendChild(item);
    });
  } else {
    factorsSection.style.display = 'none';
  }

  // Scroll to result on mobile
  if (window.innerWidth < 900) {
    document.getElementById('resultCard').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
}

function resetForm() {
  document.getElementById('predictForm').reset();
  document.getElementById('resultCard').style.display = 'none';
  document.getElementById('emptyResult').style.display = 'block';

  // Reset toggles
  document.querySelectorAll('.toggle-btn').forEach((btn, i) => {
    btn.classList.toggle('active', i === 0);
  });
  extracurricularValue = 0;
  document.getElementById('extracurricular').value = '0';
}

function showError(msg) {
  alert('Error: ' + msg);
}

function shakeForm() {
  const form = document.getElementById('predictForm');
  form.style.animation = 'none';
  form.offsetHeight; // reflow
  form.style.animation = 'shake 0.4s ease';
}

// Add shake animation dynamically
const style = document.createElement('style');
style.textContent = `
  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    20%, 60% { transform: translateX(-6px); }
    40%, 80% { transform: translateX(6px); }
  }
`;
document.head.appendChild(style);

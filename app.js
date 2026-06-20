const views = document.querySelectorAll(".view");
const navButtons = document.querySelectorAll(".nav-btn");
const moduleButtons = document.querySelectorAll(".module-card");
const backButtons = document.querySelectorAll(".back-btn");

const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const chatWindow = document.getElementById("chatWindow");
const memoryOrbit =
    document.getElementById("memoryOrbit");
const memoryNodes = document.getElementById("memoryNodes");
const toolNodes = document.getElementById("toolNodes");
const complexityValue = document.getElementById("complexityValue");
const complexityBar = document.getElementById("complexityBar");
const awarenessLabel =
    document.getElementById("awarenessLabel");
const memoryList = document.getElementById("memoryList");
const toolsList = document.getElementById("toolsList");

function showView(viewId) {
  views.forEach(v => v.classList.remove("active"));
  document.getElementById(viewId)?.classList.add("active");

  navButtons.forEach(btn => {
    btn.classList.remove("active");
    if (btn.dataset.target === viewId) {
      btn.classList.add("active");
    }
  });
}

navButtons.forEach(btn => {
  btn.addEventListener("click", () => {
    showView(btn.dataset.target);
  });
});

moduleButtons.forEach(btn => {
  btn.addEventListener("click", () => {
    showView(btn.dataset.target);
  });
});

backButtons.forEach(btn => {
  btn.addEventListener("click", () => {
    showView(btn.dataset.target);
  });
});

async function loadCore() {
  try {
    const response = await fetch("/core");
    const data = await response.json();

    memoryNodes.textContent = data.memory_nodes;
    toolNodes.textContent = data.tool_nodes;

    complexityValue.textContent =
      `${data.neural_complexity}%`;

    complexityBar.style.width =
      `${data.neural_complexity}%`;

if (awarenessLabel) {
    awarenessLabel.textContent =
        `ASTRA AWARENESS ${data.neural_complexity}%`;
}
  } catch (err) {
    console.error(err);
  }
}

async function loadMemories() {
  try {
    const response = await fetch("/memories");
    const data = await response.json();

    if (!data.memories || data.memories.length === 0) {
      memoryList.innerHTML =
        `<div class="empty-state">
          Noch keine Erinnerungen gespeichert.
        </div>`;
      return;
    }

    memoryList.innerHTML = data.memories
      .slice()
      .reverse()
      .map(memory => `
        <div class="module-card">
          <strong>Memory</strong>
          <small>${memory}</small>
        </div>
      `)
      .join("");

  } catch (err) {
    console.error(err);
  }
}

async function loadTools() {
  try {
    const response = await fetch("/tools");
    const data = await response.json();

    toolsList.innerHTML = data.tools.map(tool => `
      <div class="module-card">
        <strong>${tool.name}</strong>
        <small>Status: ${tool.status}</small>
      </div>
    `).join("");

  } catch (err) {
    console.error(err);
  }
}

function addMessage(text, type = "nova") {
  const div = document.createElement("div");

  div.className =
    type === "user"
      ? "user-message"
      : "nova-message";

  div.textContent = text;

  chatWindow.appendChild(div);

  chatWindow.scrollTop =
    chatWindow.scrollHeight;
}

chatForm?.addEventListener("submit", async (e) => {
  e.preventDefault();

  const prompt = chatInput.value.trim();

  if (!prompt) return;

  addMessage(prompt, "user");
  chatInput.value = "";
setThinkingMode(true);
  try {
    const response = await fetch("/ask", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        prompt
      })
    });

    const data = await response.json();

    addMessage(
      data.result || "Keine Antwort erhalten."
    );

    if (data.core) {
      complexityValue.textContent =
        `${data.core.neural_complexity}%`;

      complexityBar.style.width =
        `${data.core.neural_complexity}%`;

      memoryNodes.textContent =
        data.core.memory_nodes;

      toolNodes.textContent =
        data.core.tool_nodes;
    }

    loadMemories();
setThinkingMode(false);
  } catch (err) {
    addMessage(
      "Verbindung zu NOVA fehlgeschlagen."
    );

    console.error(err);
setThinkingMode(false);
  }
});

/* ==========================
   NOVA Neural Background V2
========================== */

const canvas = document.getElementById("coreCanvas");
const ctx = canvas.getContext("2d");

let particles = [];
let pulses = [];
let thinkingMode = false;

function resize() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
}

window.addEventListener("resize", resize);
resize();

function createParticles() {
  particles = [];

  const count = Math.min(120, Math.floor((canvas.width * canvas.height) / 9000));

  for (let i = 0; i < count; i++) {
    const colors = [
      "rgba(0,207,255,0.85)",
      "rgba(139,92,246,0.75)",
      "rgba(255,209,102,0.75)"
    ];

    particles.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      r: Math.random() * 2.2 + 0.7,
      dx: (Math.random() - 0.5) * 0.55,
      dy: (Math.random() - 0.5) * 0.55,
      color: colors[Math.floor(Math.random() * colors.length)],
      glow: Math.random() * 10 + 6
    });
  }
}

createParticles();

function spawnPulse() {
  const centerX = canvas.width / 2;
  const centerY = canvas.height * 0.38;

  pulses.push({
    x: Math.random() * canvas.width,
    y: Math.random() * canvas.height,
    tx: centerX + (Math.random() - 0.5) * 120,
    ty: centerY + (Math.random() - 0.5) * 120,
    life: 1,
    speed: thinkingMode ? 0.035 : 0.018,
    color: Math.random() > 0.45
      ? "rgba(255,209,102,0.95)"
      : "rgba(0,207,255,0.9)"
  });
}

function animate() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const centerX = canvas.width / 2;
  const centerY = canvas.height * 0.38;

  particles.forEach(p => {
    const pull = thinkingMode ? 0.0009 : 0.00025;

    p.dx += (centerX - p.x) * pull;
    p.dy += (centerY - p.y) * pull;

    p.x += p.dx;
    p.y += p.dy;

    p.dx *= 0.985;
    p.dy *= 0.985;

    if (p.x < 0 || p.x > canvas.width) p.dx *= -1;
    if (p.y < 0 || p.y > canvas.height) p.dy *= -1;

    ctx.save();
    ctx.beginPath();
    ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
    ctx.fillStyle = p.color;
    ctx.shadowBlur = p.glow;
    ctx.shadowColor = p.color;
    ctx.fill();
    ctx.restore();
  });

  for (let a = 0; a < particles.length; a++) {
    for (let b = a + 1; b < particles.length; b++) {
      const dx = particles[a].x - particles[b].x;
      const dy = particles[a].y - particles[b].y;
      const dist = Math.sqrt(dx * dx + dy * dy);

      if (dist < 125) {
        ctx.save();
        ctx.beginPath();
        ctx.moveTo(particles[a].x, particles[a].y);
        ctx.lineTo(particles[b].x, particles[b].y);

        const alpha = (1 - dist / 125) * (thinkingMode ? 0.9 : 0.45);

        ctx.strokeStyle = `rgba(0,207,255,${alpha})`;
        ctx.lineWidth = thinkingMode ? 1.1 : 0.55;
        ctx.shadowBlur = thinkingMode ? 10 : 3;
        ctx.shadowColor = "rgba(0,207,255,0.8)";
        ctx.stroke();
        ctx.restore();
      }
    }
  }

  if (Math.random() < (thinkingMode ? 0.09 : 0.025)) {
    spawnPulse();
  }

  pulses.forEach(p => {
    p.x += (p.tx - p.x) * p.speed;
    p.y += (p.ty - p.y) * p.speed;
    p.life -= thinkingMode ? 0.012 : 0.008;

    ctx.save();
    ctx.beginPath();
    ctx.arc(p.x, p.y, 3.2, 0, Math.PI * 2);
    ctx.fillStyle = p.color;
    ctx.globalAlpha = Math.max(p.life, 0);
    ctx.shadowBlur = 22;
    ctx.shadowColor = p.color;
    ctx.fill();
    ctx.restore();
  });

  pulses = pulses.filter(p => p.life > 0);

  requestAnimationFrame(animate);
}

animate();

function setThinkingMode(active) {
  thinkingMode = active;
  document.body.classList.toggle("thinking", active);
}

/* Initial loading */
loadCore();
loadMemories();
loadTools();

setInterval(loadCore, 10000);
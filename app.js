const views = document.querySelectorAll(".view");
const navButtons = document.querySelectorAll(".nav-btn");
const moduleButtons = document.querySelectorAll(".module-card");
const backButtons = document.querySelectorAll(".back-btn");

const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const chatWindow = document.getElementById("chatWindow");

const memoryNodes = document.getElementById("memoryNodes");
const toolNodes = document.getElementById("toolNodes");
const complexityValue = document.getElementById("complexityValue");
const complexityBar = document.getElementById("complexityBar");

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

  } catch (err) {
    addMessage(
      "Verbindung zu NOVA fehlgeschlagen."
    );

    console.error(err);
  }
});

/* ==========================
   Neural Background
========================== */

const canvas =
  document.getElementById("coreCanvas");

const ctx =
  canvas.getContext("2d");

let particles = [];

function resize() {
  canvas.width =
    window.innerWidth;

  canvas.height =
    window.innerHeight;
}

window.addEventListener(
  "resize",
  resize
);

resize();

for (let i = 0; i < 60; i++) {
  particles.push({
    x: Math.random() * canvas.width,
    y: Math.random() * canvas.height,
    r: Math.random() * 2 + 1,
    dx: (Math.random() - 0.5) * 0.4,
    dy: (Math.random() - 0.5) * 0.4
  });
}

function animate() {
  ctx.clearRect(
    0,
    0,
    canvas.width,
    canvas.height
  );

  particles.forEach(p => {

    p.x += p.dx;
    p.y += p.dy;

    if (
      p.x < 0 ||
      p.x > canvas.width
    ) p.dx *= -1;

    if (
      p.y < 0 ||
      p.y > canvas.height
    ) p.dy *= -1;

    ctx.beginPath();
    ctx.arc(
      p.x,
      p.y,
      p.r,
      0,
      Math.PI * 2
    );

    ctx.fillStyle =
      "rgba(0,207,255,0.7)";

    ctx.fill();
  });

  for (let a = 0; a < particles.length; a++) {
    for (
      let b = a + 1;
      b < particles.length;
      b++
    ) {

      const dx =
        particles[a].x -
        particles[b].x;

      const dy =
        particles[a].y -
        particles[b].y;

      const dist =
        Math.sqrt(
          dx * dx +
          dy * dy
        );

      if (dist < 120) {
        ctx.beginPath();

        ctx.moveTo(
          particles[a].x,
          particles[a].y
        );

        ctx.lineTo(
          particles[b].x,
          particles[b].y
        );

        ctx.strokeStyle =
          `rgba(139,92,246,${
            1 - dist / 120
          })`;

        ctx.stroke();
      }
    }
  }

  requestAnimationFrame(
    animate
  );
}

animate();

loadCore();
loadMemories();
loadTools();

setInterval(loadCore, 10000);
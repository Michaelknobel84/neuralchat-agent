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

const awarenessLabel =
    document.getElementById("awarenessLabel");

const memoryOrbit = document.getElementById("memoryOrbit");
const memoryList = document.getElementById("memoryList");

const toolsList = document.getElementById("toolsList");
const actionList = document.getElementById("actionList");

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
  <div class="agent-card">
    <div class="agent-icon">
      ${tool.id === "coding_agent" ? "🤖" : "⚙️"}
    </div>

    <div>
      <strong>${tool.name}</strong>
      <small>Status: ${tool.status}</small>
      ${tool.description ? `<p>${tool.description}</p>` : ""}
    </div>
  </div>
`).join("");

  } catch (err) {
    console.error(err);
  }
}

async function loadActions() {

    if (!actionList) return;

    try {
        const response = await fetch("/logs");
        const logs = await response.json();

        if (!logs.length) {
            actionList.innerHTML =
                '<div class="empty-state">Noch keine Aktionen protokolliert.</div>';
            return;
        }

        actionList.innerHTML = "";

        logs.reverse().forEach(log => {

            const div = document.createElement("div");

            div.className =
                `action-item risk-${log.risk}`;

            div.innerHTML = `
                <strong>${log.action_type}</strong>
                <div>${log.description}</div>
                <small>
                    ${log.risk.toUpperCase()}
                </small>
            `;

            actionList.appendChild(div);
        });

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
let dataArms = [];
let neuralNodes = [];
let thinkingMode = false;
let astraAwareness = 14;

function resize() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;

  createParticles?.();
  createDataArms?.();
  createNeuralNodes?.();
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
function createDataArms() {
  dataArms = [];

  const arms = 12;

  for (let i = 0; i < arms; i++) {
    dataArms.push({
      angle: (Math.PI * 2 / arms) * i,
      offset: Math.random() * Math.PI * 2,
      speed: 0.006 + Math.random() * 0.004,
      length: 170 + Math.random() * 120,
      color: i % 2 === 0
        ? "rgba(0,207,255,0.75)"
        : "rgba(139,92,246,0.65)"
    });
  }
}

createDataArms();

function createNeuralNodes() {
  neuralNodes = [];

  const centerX = canvas.width / 2;
  const centerY = canvas.height * 0.48;

  const count = 42;

  for (let i = 0; i < count; i++) {
    const angle = Math.random() * Math.PI * 2;
    const radius = 80 + Math.random() * 190;

    neuralNodes.push({
      x: centerX + Math.cos(angle) * radius,
      y: centerY + Math.sin(angle) * radius,
      baseX: centerX + Math.cos(angle) * radius,
      baseY: centerY + Math.sin(angle) * radius,
      r: Math.random() * 1.8 + 1,
      phase: Math.random() * Math.PI * 2,
      speed: 0.008 + Math.random() * 0.008,
      color: Math.random() > 0.35
        ? "rgba(0,207,255,0.9)"
        : "rgba(139,92,246,0.85)"
    });
  }
}

createNeuralNodes();

function animate() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const centerX = canvas.width / 2;
  const centerY = canvas.height * 0.38;

dataArms.forEach(arm => {
  const time = Date.now() * arm.speed;

  const startRadius = 105;
  const endRadius = arm.length;

  const strands = 4;

  for (let s = 0; s < strands; s++) {
    const strandOffset = (s - 1.5) * 0.045;
    const wobble = Math.sin(time + arm.offset + s) * 0.22;

    const angle = arm.angle + wobble + strandOffset;

    const startX = centerX + Math.cos(angle) * startRadius;
    const startY = centerY + Math.sin(angle) * startRadius;

    const endX = centerX + Math.cos(angle) * endRadius;
    const endY = centerY + Math.sin(angle) * endRadius;

    const controlX =
      centerX + Math.cos(angle + 0.45) * (endRadius * 0.62);

    const controlY =
      centerY + Math.sin(angle + 0.45) * (endRadius * 0.62);

    ctx.save();
    ctx.beginPath();
    ctx.moveTo(startX, startY);
    ctx.quadraticCurveTo(controlX, controlY, endX, endY);

    ctx.strokeStyle = arm.color;
    ctx.lineWidth = thinkingMode ? 0.9 : 0.42;
    ctx.globalAlpha = thinkingMode ? 0.72 : 0.32;
    ctx.shadowBlur = thinkingMode ? 18 : 9;
    ctx.shadowColor = arm.color;
    ctx.stroke();
    ctx.restore();

    const packetProgress =
      (time * 0.55 + arm.offset + s * 0.18) % 1;

    const packetX =
      startX + (endX - startX) * packetProgress;

    const packetY =
      startY + (endY - startY) * packetProgress;

    ctx.save();
    ctx.beginPath();
    ctx.arc(packetX, packetY, thinkingMode ? 2.4 : 1.6, 0, Math.PI * 2);
    ctx.fillStyle = arm.color;
    ctx.globalAlpha = thinkingMode ? 0.9 : 0.55;
    ctx.shadowBlur = 18;
    ctx.shadowColor = arm.color;
    ctx.fill();
    ctx.restore();
  }
});

  const startRadius = 95;
  const endRadius = arm.length;

  const wobble =
    Math.sin(time + arm.offset) * 0.35;

  const angle =
    arm.angle + wobble;

  const startX =
    centerX + Math.cos(angle) * startRadius;

  const startY =
    centerY + Math.sin(angle) * startRadius;

  const endX =
    centerX + Math.cos(angle) * endRadius;

  const endY =
    centerY + Math.sin(angle) * endRadius;

  const midX =
    centerX + Math.cos(angle) * (endRadius * 0.45);

  const midY =
    centerY + Math.sin(angle) * (endRadius * 0.45);

  ctx.save();
  ctx.beginPath();
  ctx.moveTo(startX, startY);
  ctx.quadraticCurveTo(midX, midY, endX, endY);

  ctx.strokeStyle = arm.color;
  ctx.lineWidth = thinkingMode ? 1.2 : 0.55;
  ctx.shadowBlur = thinkingMode ? 24 : 14;
  ctx.shadowColor = arm.color;
  ctx.globalAlpha = thinkingMode ? 0.65 : 0.28;

  ctx.stroke();
  ctx.restore();

  const packetProgress =
    (time + arm.offset) % 1;

  const packetX =
    startX + (endX - startX) * packetProgress;

  const packetY =
    startY + (endY - startY) * packetProgress;

  ctx.save();
  ctx.beginPath();
  ctx.arc(packetX, packetY, 2.2, 0, Math.PI * 2);
  ctx.fillStyle = arm.color;
  ctx.shadowBlur = 22;
  ctx.shadowColor = arm.color;
  ctx.fill();
  ctx.restore();
});

neuralNodes.forEach(node => {
  const t = Date.now() * node.speed;

  node.x = node.baseX + Math.cos(t + node.phase) * 12;
  node.y = node.baseY + Math.sin(t + node.phase) * 12;

  ctx.save();
  ctx.beginPath();
  ctx.arc(node.x, node.y, node.r, 0, Math.PI * 2);
  ctx.fillStyle = node.color;
  ctx.shadowBlur = 18;
  ctx.shadowColor = node.color;
  ctx.fill();
  ctx.restore();
});

for (let i = 0; i < neuralNodes.length; i++) {
  for (let j = i + 1; j < neuralNodes.length; j++) {
    const dx = neuralNodes[i].x - neuralNodes[j].x;
    const dy = neuralNodes[i].y - neuralNodes[j].y;
    const dist = Math.sqrt(dx * dx + dy * dy);

  if (
      dist < 95 &&
      Math.hypot(neuralNodes[i].x - centerX, neuralNodes[i].y - centerY) > 125 &&
      Math.hypot(neuralNodes[j].x - centerX, neuralNodes[j].y - centerY) > 125
) {
      ctx.save();
      ctx.beginPath();
      ctx.moveTo(neuralNodes[i].x, neuralNodes[i].y);
      ctx.lineTo(neuralNodes[j].x, neuralNodes[j].y);

      const alpha = (1 - dist / 95) * 0.35;

      ctx.strokeStyle = `rgba(0,207,255,${alpha})`;
      ctx.lineWidth = 0.45;
      ctx.shadowBlur = 8;
      ctx.shadowColor = "rgba(0,207,255,0.7)";
      ctx.stroke();
      ctx.restore();
    }
  }
}

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
loadActions();

setInterval(loadCore, 10000);
function updateMemoryNodes(count) {

    if (!memoryOrbit) return;

    memoryOrbit.innerHTML = "";

    const radius = 120;

    for (let i = 0; i < count; i++) {

        const angle = (Math.PI * 2 / count) * i;

        const x = Math.cos(angle) * radius + 135;
        const y = Math.sin(angle) * radius + 135;

        const node = document.createElement("div");

        node.className = "memory-node";

        node.style.left = `${x}px`;
        node.style.top = `${y}px`;

        memoryOrbit.appendChild(node);
    }
}
const analyzeBtn =
    document.getElementById("analyzeCodeBtn");

const codeInput =
    document.getElementById("codeInput");

const codeResult =
    document.getElementById("codeResult");

if (analyzeBtn) {

    analyzeBtn.addEventListener("click", async () => {

        const code = codeInput.value.trim();

        if (!code) {
            codeResult.innerHTML =
                "Bitte zuerst Code eingeben.";
            return;
        }

        codeResult.innerHTML =
            "Coding Agent analysiert...";

        try {

            const response = await fetch(
                "/coding-agent/analyze",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        code: code,
                        question: "Prüfe diesen Code."
                    })
                }
            );

            const data = await response.json();

            codeResult.innerHTML =
                data.result;

        } catch (err) {

            codeResult.innerHTML =
                "Analyse fehlgeschlagen.";

            console.error(err);
        }
    });
}
const imagePrompt =
    document.getElementById("imagePrompt");

const imageStyle =
    document.getElementById("imageStyle");

const generateImageBtn =
    document.getElementById("generateImageBtn");

const copyPromptBtn =
    document.getElementById("copyPromptBtn");

if (generateImageBtn) {
    generateImageBtn.addEventListener("click", () => {
        const prompt = imagePrompt.value.trim();
        const style = imageStyle.value;

        if (!prompt) {
            imageResult.innerHTML =
                "Bitte zuerst eine Bildbeschreibung eingeben.";
            return;
        }

        let enhancedPrompt = prompt;

        if (style === "nova") {
            enhancedPrompt =
                `${prompt}, futuristic NOVA neural core, holographic sci-fi interface, cyan and violet energy, cinematic lighting, ultra detailed`;
        }

        if (style === "neural") {
            enhancedPrompt =
                `${prompt}, neural network, glowing synapses, data streams, cybernetic intelligence, high detail`;
        }

        if (style === "holographic") {
            enhancedPrompt =
                `${prompt}, holographic projection, transparent light layers, futuristic HUD, blue violet glow`;
        }

        if (style === "cinematic") {
            enhancedPrompt =
                `${prompt}, cinematic composition, dramatic lighting, ultra realistic, high contrast`;
        }

        if (style === "custom") {
            enhancedPrompt = prompt;
        }

        imageResult.innerHTML = `
            <strong>Vorbereiteter Prompt:</strong>
            <br><br>
            ${enhancedPrompt}
        `;
    });
}

if (copyPromptBtn) {

    copyPromptBtn.addEventListener("click", () => {

        const text =
            imageResult.innerText;

        navigator.clipboard.writeText(text);

        copyPromptBtn.innerHTML =
            "✅ Kopiert";

        setTimeout(() => {
            copyPromptBtn.innerHTML =
                "📋 Prompt kopieren";
        }, 2000);
    });
}

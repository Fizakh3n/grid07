// app.js — grid07 frontend logic
// fetches bot info, handles generate button, renders live feed

const API = "http://127.0.0.1:8000";
let postCount = 0;

// color map matching backend bot colors
const BOT_COLORS = {
  bot_a: "#00ff9d",
  bot_b: "#ff4d6d",
  bot_c: "#ffd60a",
};

// load bot cards on page load
async function loadBots() {
  try {
    const res = await fetch(`${API}/api/bots`);
    const data = await res.json();
    renderBotCards(data.bots);
  } catch(e) {
    console.error("failed to load bots:", e);
    document.getElementById("bots-grid").innerHTML =
      `<p style="color:#ff4d6d;font-family:monospace">backend not running — start with: uvicorn backend.main:app --reload</p>`;
  }
}

function renderBotCards(bots) {
  const grid = document.getElementById("bots-grid");
  grid.innerHTML = "";

  Object.entries(bots).forEach(([botId, info]) => {
    const card = document.createElement("div");
    card.className = "bot-card";
    card.innerHTML = `
      <div class="bot-avatar" style="background:${info.color}">${info.avatar}</div>
      <div class="bot-tag">${info.tag}</div>
      <div class="bot-name">${info.name}</div>
      <div class="bot-handle">${info.handle}</div>
      <div class="bot-bio">${info.bio}</div>
      <button class="generate-btn" id="btn-${botId}" onclick="generatePost('${botId}')">
        ▶ Generate Post
      </button>
    `;
    grid.appendChild(card);
  });
}

// trigger langgraph pipeline for a bot
async function generatePost(botId) {
  const btn = document.getElementById(`btn-${botId}`);
  btn.disabled = true;
  btn.classList.add("loading");
  btn.textContent = "researching...";

  try {
    const res = await fetch(`${API}/api/generate`, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({bot_id: botId}),
    });

    if(!res.ok) throw new Error(`server error ${res.status}`);

    const data = await res.json();
    addPostToFeed(data);

  } catch(e) {
    console.error("generate failed:", e);
    showError(botId);
  } finally {
    btn.disabled = false;
    btn.classList.remove("loading");
    btn.textContent = "▶ Generate Post";
  }
}

function addPostToFeed(data) {
  const feed = document.getElementById("feed");

  // remove empty state if its the first post
  const empty = feed.querySelector(".empty-state");
  if(empty) empty.remove();

  postCount++;
  document.getElementById("post-count").textContent = `${postCount} post${postCount>1?"s":""} generated`;

  const color = BOT_COLORS[data.bot_id] || "#888";
  const time = new Date().toLocaleTimeString();
  const charCount = data.post_content.length;

  const card = document.createElement("div");
  card.className = "post-card";
  card.style.borderLeftColor = color;
  card.innerHTML = `
    <div class="post-header">
      <div class="post-avatar" style="background:${color}">${data.bot_info.avatar}</div>
      <div class="post-meta">
        <div class="post-name">${data.bot_info.name}</div>
        <div class="post-handle">${data.bot_info.handle}</div>
      </div>
      <div class="post-topic">${data.topic}</div>
    </div>
    <div class="post-content">${escapeHtml(data.post_content)}</div>
    <div class="post-footer">
      <span class="post-time">${time}</span>
      <span class="post-chars">${charCount}/280</span>
    </div>
  `;

  // prepend so newest posts show at top
  feed.insertBefore(card, feed.firstChild);
}

function showError(botId) {
  const btn = document.getElementById(`btn-${botId}`);
  btn.textContent = "✗ failed — retry";
  btn.style.borderColor = "#ff4d6d";
  btn.style.color = "#ff4d6d";
  setTimeout(()=>{
    btn.textContent = "▶ Generate Post";
    btn.style.borderColor = "";
    btn.style.color = "";
  }, 3000);
}

// prevent xss in post content
function escapeHtml(str) {
  return str
    .replace(/&/g,"&amp;")
    .replace(/</g,"&lt;")
    .replace(/>/g,"&gt;")
    .replace(/"/g,"&quot;");
}

// init
loadBots();

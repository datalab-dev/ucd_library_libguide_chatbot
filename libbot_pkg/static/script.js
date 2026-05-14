// -------------------------------------------------------
// Streams HTML token by token
// -------------------------------------------------------
function typeHTML(element, html, speed = 10) {
  const tokens = html.match(/(<[^>]+>|[^<]+)/g);
  let i = 0;
  let currentParent = element;

  function typeToken() {
    if (i >= tokens.length) return;
    const token = tokens[i];

    if (token.startsWith("<")) {
      if (token === "<br>" || token === "<br/>") {
        currentParent.appendChild(document.createElement("br"));
      } else if (token.startsWith("</")) {
        currentParent = element;
      } else {
        const tagMatch = token.match(/^<(\w+)/);
        if (tagMatch) {
          const newTag = document.createElement(tagMatch[1]);
          currentParent.appendChild(newTag);
          currentParent = newTag;
        } else {
          currentParent.innerHTML += token;
        }
      }
      i++;
      typeToken();
    } else {
      let j = 0;
      const span = document.createElement("span");
      currentParent.appendChild(span);
      function typeChar() {
        if (j < token.length) {
          span.textContent += token.charAt(j);
          j++;
          setTimeout(typeChar, speed);
        } else {
          i++;
          typeToken();
        }
      }
      typeChar();
    }
  }
  typeToken();
}

// -------------------------------------------------------
// Build the sources section HTML from the RAG payload
// -------------------------------------------------------
function buildSourcesHTML(ragResults) {
  let html =
    `<br><br><br><br><strong>Reliable LibGuide resources from the UC Davis Library:</strong><br>` +
    `<i>(Some resource links may require you to be signed into Kerberos or on ` +
    `the UC Davis Library VPN)</i><br><br>`;

  const grouped = new Map();

  ragResults.forEach((result, index) => {
    result.sources.forEach(src => {
      // Version 5 - Group by LibGuide, then list all resources under each guide
      if (!grouped.has(src.libguide_title)) {
        grouped.set(src.libguide_title, {
          section_url: src.section_url,
          resources: new Map(),
        });
      }
      grouped.get(src.libguide_title).resources.set(src.section_title, {
        external_url: src.external_url,
        section_url: src.section_url,
      });
    });
  });

  grouped.forEach((guide, title) => {
    html += `• <a href="${guide.section_url}" target="_blank"><strong>${title}</strong></a><br>`;
    guide.resources.forEach((urls, section_title) => {
      html += `&nbsp;&nbsp;&nbsp;&nbsp;↳ <a href="${urls.external_url}" target="_blank">${section_title}</a><br>`;
    });
    html += `<br>`;
  });

  return html;
}

// -------------------------------------------------------
// Welcome screen → chat swap on first message
// -------------------------------------------------------
let chatStarted = false;

function activateChat() {
  if (chatStarted) return;
  chatStarted = true;
  document.getElementById("welcome-screen").classList.add("hidden");
  document.getElementById("chat-main").classList.remove("hidden");
}

// -------------------------------------------------------
// Send message — handles streaming response
// -------------------------------------------------------
async function sendMessage() {
  const welcomeInput = document.getElementById("welcome-user-input");
  const chatInput = document.getElementById("user-input");

  const activeInput = chatStarted ? chatInput : welcomeInput;
  const userMessage = activeInput.value.trim();
  if (!userMessage) return;
  activeInput.value = "";
  activeInput.style.height = "auto";
  activeInput.style.overflowY = "hidden";

  activateChat();

  const chatBox = document.getElementById("chat-box");

  const userDiv = document.createElement("div");
  userDiv.className = "message user";
  const userBubble = document.createElement("span");
  userBubble.className = "user-bubble";
  userBubble.textContent = userMessage;
  userDiv.appendChild(userBubble);
  chatBox.appendChild(userDiv);

  const botDiv = document.createElement("div");
  botDiv.className = "message bot";
  const botLabel = document.createElement("div");
  botLabel.className = "bot-label";
  botLabel.textContent = "LibBot";
  botDiv.appendChild(botLabel);
  chatBox.appendChild(botDiv);

  const statusDiv = document.createElement("div");
  statusDiv.className = "loading-status";
  statusDiv.innerHTML = `<div class="loading-spinner"></div><span class="status-text">Scanning sources...</span>`;
  chatBox.appendChild(statusDiv);

  const phrases = ["Finding relevant info...", "Sifting through pages...", "Connecting the dots...", "Formulating answer..."];
  let phraseIdx = 0;
  const phraseInterval = setInterval(() => {
    const textSpan = statusDiv.querySelector(".status-text");
    if (textSpan) textSpan.textContent = phrases[phraseIdx++ % phrases.length];
  }, 3000);

  const llmSpan = document.createElement("span");
  botDiv.appendChild(llmSpan);

  const sourcesDiv = document.createElement("div");
  botDiv.appendChild(sourcesDiv);

  chatBox.scrollTop = chatBox.scrollHeight;

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: userMessage, top_k: 3 }),
    });

    if (!response.ok) {
      throw new Error(`Server returned ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    let sourcesRendered = false;
    let fullLLMResponse = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      if (!sourcesRendered && buffer.includes("\n")) {
        const newlineIndex = buffer.indexOf("\n");
        const firstLine = buffer.slice(0, newlineIndex);
        buffer = buffer.slice(newlineIndex + 1);

        if (firstLine.startsWith("SOURCES:")) {
          try {
            sourcesDiv._ragResults = JSON.parse(firstLine.slice("SOURCES:".length));
            sourcesRendered = true;
          } catch (e) { console.error("Source parse error", e); }
        }
      }

      if (sourcesRendered && buffer.length > 0) {
        if (statusDiv && statusDiv.parentNode) {
          clearInterval(phraseInterval);
          statusDiv.remove();
          llmSpan.classList.add("fade-in-text");
        }

        fullLLMResponse += buffer;
        buffer = "";

        const rawHtml = marked.parse(fullLLMResponse);
        llmSpan.innerHTML = DOMPurify.sanitize(rawHtml);

        chatBox.scrollTop = chatBox.scrollHeight;
      }
    }

    try {
      if (sourcesDiv._ragResults) {
        console.log("RAG results:", JSON.stringify(sourcesDiv._ragResults, null, 2));
        sourcesDiv.innerHTML = buildSourcesHTML(sourcesDiv._ragResults);
      }
    } catch (e) {
      console.error("Failed to render sources:", e);
      sourcesDiv.textContent = "(Could not render sources)";
    }

  } catch (error) {
    console.error("Fetch error:", error);
    botDiv.textContent = "Failed to reach the server. Please try again.";
  }

  chatBox.scrollTop = chatBox.scrollHeight;
}

// -------------------------------------------------------
// Evil mode easter egg — type console.log(67) in DevTools
// -------------------------------------------------------
let evilMode = false;
const logo = document.getElementById("logo");
const welcomeLogo = document.getElementById("welcome-logo");

function toggleEvilMode() {
  evilMode = !evilMode;
  document.body.classList.toggle("evil", evilMode);

  if (evilMode) {
    welcomeLogo.src = "assets/logo-dark.svg";
  } else {
    const isDark = document.body.classList.contains("dark");
    welcomeLogo.src = isDark ? "assets/logo-dark.svg" : "assets/logo-light-transparent.svg";
  }
}

const _origConsoleLog = console.log;
console.log = function (...args) {
  if (args.length === 1 && (args[0] === 67 || args[0] === "67")) {
    toggleEvilMode();
    _origConsoleLog.call(console, `[evil mode ${evilMode ? "ON" : "OFF"}]`);
    return;
  }
  _origConsoleLog.apply(console, args);
};

// -------------------------------------------------------
// Dark mode toggle
// -------------------------------------------------------
const modeToggle = document.getElementById("mode-toggle");
const iconMoon = document.getElementById("icon-moon");
const iconSun = document.getElementById("icon-sun");

modeToggle.addEventListener("click", () => {
  document.body.classList.toggle("dark");
  const isDark = document.body.classList.contains("dark");

  iconMoon.style.display = isDark ? "none" : "block";
  iconSun.style.display  = isDark ? "block" : "none";

  logo.src = isDark ? "assets/datalab-logo-gold.svg" : "assets/datalab-logo-black.svg";

  if (!evilMode) {
    welcomeLogo.src = isDark ? "assets/logo-dark.svg" : "assets/logo-light-transparent.svg";
  }
});

// -------------------------------------------------------
// Enter key to send
// -------------------------------------------------------
function autoResizeTextarea(el) {
  el.style.height = "auto";
  const capped = Math.min(el.scrollHeight, 140);
  el.style.height = capped + "px";
  el.style.overflowY = el.scrollHeight > 140 ? "auto" : "hidden";
}

document.addEventListener("DOMContentLoaded", function () {
  ["user-input", "welcome-user-input"].forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;

    el.addEventListener("keydown", function (event) {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
      }
    });

    el.addEventListener("input", function () {
      autoResizeTextarea(el);
    });
  });
});

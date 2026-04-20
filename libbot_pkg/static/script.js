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
    `<br><br><br><br><strong>Reliable resources from the UC Davis Library:</strong><br>` +
    `<i>(Some resource links may require you to be signed into Kerberos or on ` +
    `the UC Davis Library VPN)</i><br><br>`;

  ragResults.forEach((result, index) => {
    result.sources.forEach(src => {
      // Each source may have multiple URLs (libguide, section, external), so we list them all under the same titl
      // This can be edited to only include one type of URL for each source if desired
      html += `• <strong>${src.libguide_title}</strong> → ${src.section_title}<br>`;
      html += `<a href="${src.libguide_url}" target="_blank">LibGuide</a><br>`;
      html += `<a href="${src.section_url}" target="_blank">Section</a><br>`;
      html += `<a href="${src.external_url}" target="_blank">External resource</a><br>`;
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
  document.getElementById("welcome-input").classList.add("hidden");
  document.getElementById("chat-main").classList.remove("hidden");
}

// -------------------------------------------------------
// Send message — handles streaming response
// -------------------------------------------------------
async function sendMessage() {
  // Support both the welcome input and the chat input
  const welcomeInput = document.getElementById("welcome-user-input");
  const chatInput = document.getElementById("user-input");

  // Grab text from whichever input is active
  const activeInput = chatStarted ? chatInput : welcomeInput;
  const userMessage = activeInput.value.trim();
  if (!userMessage) return;
  activeInput.value = "";

  // Switch from welcome screen to chat on first send
  activateChat();

  const chatBox = document.getElementById("chat-box");

  // Display user message as a styled bubble
  const userDiv = document.createElement("div");
  userDiv.className = "message user";
  const userBubble = document.createElement("span");
  userBubble.className = "user-bubble";
  userBubble.textContent = userMessage;
  userDiv.appendChild(userBubble);
  chatBox.appendChild(userDiv);

  // Bot message container
  const botDiv = document.createElement("div");
  botDiv.className = "message bot";
  chatBox.appendChild(botDiv);

  // LLM text streams into this span
  const llmSpan = document.createElement("span");
  botDiv.appendChild(llmSpan);

  // Sources rendered after LLM is done
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
            const ragResults = JSON.parse(firstLine.slice("SOURCES:".length));
            sourcesRendered = true;
            sourcesDiv._ragResults = ragResults;
          } catch (e) {
            console.error("Failed to parse sources:", e);
          }
        }
      }

      if (sourcesRendered && buffer.length > 0) {
        llmSpan.textContent += buffer;
        buffer = "";
        chatBox.scrollTop = chatBox.scrollHeight;
      }
    }

    // Render sources as plain HTML so links are clickable
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
    botDiv.textContent = "⚠️ Failed to reach server.";
  }

  chatBox.scrollTop = chatBox.scrollHeight;
}

// -------------------------------------------------------
// Dark mode toggle
// -------------------------------------------------------
const modeToggle = document.getElementById("mode-toggle");
const logo = document.getElementById("logo");
const welcomeLogo = document.getElementById("welcome-logo");

modeToggle.addEventListener("click", () => {
  document.body.classList.toggle("dark");
  const isDark = document.body.classList.contains("dark");
  modeToggle.textContent = isDark ? "☀️ Light Mode" : "🌙 Dark Mode";
  logo.src = isDark ? "assets/datalab-logo-gold.svg" : "assets/datalab-logo-black.svg";
  welcomeLogo.src = isDark ? "assets/logo-dark.svg" : "assets/logo-light-transparent.svg";
});

// -------------------------------------------------------
// Enter key to send
// -------------------------------------------------------
document.addEventListener("DOMContentLoaded", function () {
  // Wire Enter key for both inputs
  ["user-input", "welcome-user-input"].forEach(id => {
    const input = document.getElementById(id);
    if (input) {
      input.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
          event.preventDefault();
          sendMessage();
        }
      });
    }
  });
});
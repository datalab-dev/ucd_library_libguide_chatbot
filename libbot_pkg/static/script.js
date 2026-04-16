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
    `<br><strong>Reliable resources from the UC Davis Library:</strong><br>` +
    `<i>(Some resource links may require you to be signed into Kerberos or on ` +
    `the UC Davis Library VPN)</i><br><br>`;

  ragResults.forEach((result, index) => {
    html += `<strong>Result ${index + 1}</strong> `;
    html += `<span style="color: gray;">(score: ${result.score.toFixed(4)})</span><br>`;
    html += `${result.text}<br><br>`;
    html += `<em>Found in ${result.sources.length} guide(s):</em><br>`;
    result.sources.forEach(src => {
      html += `&nbsp;&nbsp;• <strong>${src.libguide_title}</strong> → ${src.section_title}<br>`;
      html += `&nbsp;&nbsp;&nbsp;&nbsp;<a href="${src.url}" target="_blank">${src.url}</a><br>`;
    });
    html += `<br>`;
  });

  html += `=============================================================================`;
  return html;
}

// -------------------------------------------------------
// Send message — handles streaming response
// -------------------------------------------------------
async function sendMessage() {
  const inputBox = document.getElementById("user-input");
  const chatBox = document.getElementById("chat-box");
  const userMessage = inputBox.value.trim();
  if (!userMessage) return;

  // Display user message
  const userDiv = document.createElement("div");
  userDiv.className = "message user";
  userDiv.textContent = userMessage;
  chatBox.appendChild(userDiv);
  inputBox.value = "";

  // Bot message container — we'll fill this as the stream arrives
  const botDiv = document.createElement("div");
  botDiv.className = "message bot";
  chatBox.appendChild(botDiv);

  // LLM text will stream into this span
  const llmSpan = document.createElement("span");
  botDiv.appendChild(llmSpan);

  // Sources section rendered after LLM is done
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

    // Read the stream chunk by chunk
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    let sourcesRendered = false;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      // The first line is always the SOURCES: payload — parse it out
      if (!sourcesRendered && buffer.includes("\n")) {
        const newlineIndex = buffer.indexOf("\n");
        const firstLine = buffer.slice(0, newlineIndex);
        buffer = buffer.slice(newlineIndex + 1); // remainder is LLM tokens

        if (firstLine.startsWith("SOURCES:")) {
          try {
            const ragResults = JSON.parse(firstLine.slice("SOURCES:".length));
            sourcesRendered = true;
            // Don't render sources yet — append them after the LLM finishes
            // Store for later use
            sourcesDiv._ragResults = ragResults;
          } catch (e) {
            console.error("Failed to parse sources:", e);
          }
        }
      }

      // Stream remaining buffer as LLM tokens into llmSpan
      if (sourcesRendered && buffer.length > 0) {
        llmSpan.textContent += buffer;
        buffer = "";
        chatBox.scrollTop = chatBox.scrollHeight;
      }
    }

    // Once stream is done, render the sources section below the LLM reply
    if (sourcesDiv._ragResults) {
      sourcesDiv.innerHTML = ""; // clear placeholder
      typeHTML(sourcesDiv, buildSourcesHTML(sourcesDiv._ragResults), 5);
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

modeToggle.addEventListener("click", () => {
  document.body.classList.toggle("dark");
  const isDark = document.body.classList.contains("dark");
  modeToggle.textContent = isDark ? "☀️ Light Mode" : "🌙 Dark Mode";
  logo.src = isDark ? "assets/logo-dark.png" : "assets/logo-light.png";
});

// -------------------------------------------------------
// Enter key to send
// -------------------------------------------------------
document.addEventListener("DOMContentLoaded", function () {
  const inputBox = document.getElementById("user-input");
  inputBox.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
      event.preventDefault();
      sendMessage();
    }
  });
});
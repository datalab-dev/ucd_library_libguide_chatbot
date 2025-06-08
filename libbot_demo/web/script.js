function typeHTML(element, html, speed = 10) {
  const tokens = html.match(/(<[^>]+>|[^<]+)/g); // separate tags from text
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
      // Stream text content character by character
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
          typeToken(); // move to next token
        }
      }
      
      
      typeChar();
    }
  }


  typeToken();
}

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
  
    // Placeholder for bot message
    const botDiv = document.createElement("div");
    botDiv.className = "message bot";
    chatBox.appendChild(botDiv);
  
    try {
      const response = await fetch(`http://127.0.0.1:8000/?msg=${encodeURIComponent(userMessage)}`);
      const botReply = await response.text();
      
      typeHTML(botDiv, botReply, 10); // 10ms per character


      
    } catch (error) {
  console.error("Fetch error:", error);
  botDiv.textContent = "⚠️ Failed to reach server.";
    }
  }
  
  const modeToggle = document.getElementById("mode-toggle");
  const logo = document.getElementById("logo");
  
  modeToggle.addEventListener("click", () => {
    document.body.classList.toggle("dark");
  
    const isDark = document.body.classList.contains("dark");
  
    modeToggle.textContent = isDark ? "☀️ Light Mode" : "🌙 Dark Mode";
    logo.src = isDark ? "assets/logo-dark.png" : "assets/logo-light.png";
  });
  
  document.addEventListener("DOMContentLoaded", function () {
  const inputBox = document.getElementById("user-input");

  inputBox.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
      event.preventDefault(); // Prevent default behavior like submitting a form
      sendMessage(); // Call your existing sendMessage function
    }
  });
});

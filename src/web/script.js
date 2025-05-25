async function sendMessage() {
    const inputBox = document.getElementById("user-input");
    const chatBox = document.getElementById("chat-box");
    const userMessage = inputBox.value.trim();
  
    if (!userMessage) return;
  
    // Add user message
    const userDiv = document.createElement("div");
    userDiv.className = "message user";
    userDiv.textContent = userMessage;
    chatBox.appendChild(userDiv);
  
    inputBox.value = "";
  
    try {
      const response = await fetch(`http://127.0.0.1:8000/?msg=${encodeURIComponent(userMessage)}`);
      const botReply = await response.text();
  
      const botDiv = document.createElement("div");
      botDiv.className = "message bot";
      botDiv.textContent = botReply;
      chatBox.appendChild(botDiv);
      chatBox.scrollTop = chatBox.scrollHeight;
    } catch (error) {
      const errorDiv = document.createElement("div");
      errorDiv.className = "message bot";
      errorDiv.textContent = "⚠️ Failed to reach server.";
      chatBox.appendChild(errorDiv);
    }
  }
  
  const modeToggle = document.getElementById("mode-toggle");
  const logo = document.getElementById("logo");
  
  modeToggle.addEventListener("click", () => {
    document.body.classList.toggle("dark");
  
    const isDark = document.body.classList.contains("dark");
  
    modeToggle.textContent = isDark ? "☀️ Light Mode" : "🌙 Dark Mode";
    logo.src = isDark ? "assets/libbot-dark.png" : "assets/libbot-light.png";
  });
  
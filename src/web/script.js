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
  
      // Typing effect
      let i = 0;
      function typeWriter() {
        if (i < botReply.length) {
          botDiv.textContent += botReply.charAt(i);
          i++;
          chatBox.scrollTop = chatBox.scrollHeight;
          setTimeout(typeWriter, 10); // typing speed in ms
        }
      }
      typeWriter();
      
    } catch (error) {
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



// async function sendMessage() {
//     const inputBox = document.getElementById("user-input");
//     const chatBox = document.getElementById("chat-box");
//     const userMessage = inputBox.value.trim();
  
//     if (!userMessage) return;
  
//     // Add user message
//     const userDiv = document.createElement("div");
//     userDiv.className = "message user";
//     userDiv.textContent = userMessage;
//     chatBox.appendChild(userDiv);
  
//     inputBox.value = "";
  
//     try {
//       const response = await fetch(`http://127.0.0.1:8000/?prompt=${encodeURIComponent(userMessage)}`);
//       const data = await response.json();
  
//       // Add Ollama response
//       const botDiv = document.createElement("div");
//       botDiv.className = "message bot";
//       botDiv.textContent = data.ollama_reply;
//       chatBox.appendChild(botDiv);
  
//       // Add search results
//       if (data.search_results && data.search_results.length > 0) {
//         data.search_results.forEach((result) => {
//           const resultDiv = document.createElement("div");
//           resultDiv.className = "message bot result";
//           resultDiv.innerHTML = `
//             <div style="margin-top: 8px;">
//               <strong>${result.libguide_title}</strong><br>
//               <a href="${result.libguide_url}" target="_blank">${result.libguide_url}</a><br>
//               ${result.chunk_title ? `<em>${result.chunk_title}</em><br>` : ""}
//               ${result.section_url ? `<a href="${result.section_url}" target="_blank">${result.section_url}</a><br>` : ""}
//               <div style="margin-top: 4px;">${result.text}</div>
//               ${result.external_url ? `<div><a href="${result.external_url}" target="_blank">More Info</a></div>` : ""}
//             </div>
//           `;
//           chatBox.appendChild(resultDiv);
//         });
//       }
  
//       chatBox.scrollTop = chatBox.scrollHeight;
//     } catch (error) {
//       const errorDiv = document.createElement("div");
//       errorDiv.className = "message bot";
//       errorDiv.textContent = "⚠️ Failed to reach server.";
//       chatBox.appendChild(errorDiv);
//     }
//   }
  
//   // Dark/light mode toggle
//   const modeToggle = document.getElementById("mode-toggle");
//   const logo = document.getElementById("logo");
  
//   modeToggle.addEventListener("click", () => {
//     document.body.classList.toggle("dark");
  
//     const isDark = document.body.classList.contains("dark");
  
//     modeToggle.textContent = isDark ? "☀️ Light Mode" : "🌙 Dark Mode";
//     logo.src = isDark ? "assets/logo-dark.png" : "assets/logo-light.png";
//   });
  
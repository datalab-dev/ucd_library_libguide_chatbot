# LibBot: UC Davis Library Chatbot
LibBot is a search-and-response chatbot that uses a combination of large language models (LLMs) and semantic search to answer questions and suggest relevant UC Davis Library resources. It includes a backend R server and a frontend web UI.

## Project Structure
```
2025_startup_libguide_chatbot/
│
├── src/
│   └── r/
│       ├── final_demo_script.R     # Core embedding and search functions
│       └── localhost.R             # HTTP server using `httpuv`
│
├── web/
│   ├── index.html                  # Main UI
│   ├── style.css                   # Styling
│   └── script.js                   # Chat logic + animations
```
---

## Backend Setup (R Server)

### Requirements

Make sure the following R packages are installed:

- `httpuv`
- `ollamar`
- `jsonlite`
- `stringr`
- `servr`

Also, ensure [Ollama](https://ollama.com) is installed and running locally.

## Run the server:
From within R:
```
source("src/r/localhost.R")
```

The server will start on:
http://127.0.0.1:8000

---
# Frontend Setup (Web UI)
Start a local web server
From the /web directory:
```
cd web
python3 -m http.server 1234
```
Then open this in your browser:
http://127.0.0.1:1234/index.html


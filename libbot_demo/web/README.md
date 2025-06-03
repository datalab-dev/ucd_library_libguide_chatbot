# LibBot: UC Davis Library Chatbot Webpage

Before reading the specifics

LibBot is a virtual librarian search-and-response chatbot, developed to support interdisciplinary academic research by combining LLM-based responses with reliable UC Davis Library resources and research tools.

Simply put, the LibBot tool runs on a web browser page/tab found at <http://127.0.0.1:1234>, seamlessly combining two main components:

1.  `libbotR` = custom R package that matches user prompts to semantically relevant content from the UC Davis Library Guides.
2.  `Ollama` = software/app for running and managing large language models locally on your machine.

> [**This README outlines how to get the LibBot web app working (including the back-end R server and front-end web UI).**]{.underline}

------------------------------------------------------------------------

## Back-end Setup (R Server)

### Requirements

Make sure the following R packages are installed:

``` r
library(httpuv)
library(ollamar)
library(jsonlite)
library(stringr)
library(servr)
```

Also, ensure [Ollama](https://ollama.com) is installed and running locally (as outlined in the libbotR package README) + make sure to have installed the **llama3** model in an **RStudio** **Terminal** window by typing the following:

``` zsh
ollama pull llama3:8b-q3_K_M
```

### Run the server:

From within **RStudio** in the **console**:

``` r
source("insert_path_to/2025_startup_libguide_chatbot/libbot_demo/web/localhost.R")
```

(The server will start on: <http://127.0.0.1:8000>)

------------------------------------------------------------------------

## Frontend Setup (Web UI)

To get the **UI** for the web-app working, do the following:

1.  Open **RStudio** and go to the **Terminal** window.

2.  Figure out where the 2025_startup_libguide_chatbot directory is saved on your machine.

3.  Move to the /web directory inside of the 2025_startup_libguide_chatbot by typing the following:

    ``` zsh
    cd 2025_startup_libguide_chatbot/libbot_demo/web/
    ```

4.  Once you're inside of the /web directory, run the following to start up the **UI** server:

    ``` zsh
    python3 -m http.server 1234
    ```

5.  **LibBot is officially up and running!** You can find it on a browser window by typing the following:

    <http://127.0.0.1:1234>

~*A Quarter For Data Science*~

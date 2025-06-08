# LibBot: UC Davis Library Chatbot Webpage

Before reading the specifics

LibBot is a virtual librarian search-and-response chatbot, developed to support interdisciplinary academic research by combining LLM-based responses with reliable UC Davis Library resources and research tools.

Simply put, the LibBot tool runs on a browser web-app found at <http://127.0.0.1:1234>, seamlessly combining two main components:

1.  `libbotR` = custom R package that matches user prompts to semantically relevant content from the UC Davis Library Guides.
2.  `Ollama` = software/app for running and managing large language models locally on your machine.

> **This README outlines how to get the LibBot web app working (including the back-end R server and front-end web UI**

<br>

------------------------------------------------------------------------

<br>

## Back-end Setup (R Server) Dependencies:

### R Packages:

``` r
install.packages("httpuv")     ==> library(httpuv)
install.packages("jsonlite")   ==> library(jsonlite)
install.packages("stringr")    ==> library(stringr)
install.packages("servr")      ==> library(servr)
```

### Ollama App:
1. Download [Ollama](https://ollama.com/) and open it.
2. The "Welcome to Ollama" screen will pop up. Click '**install'** (and input your password if needed)
3. The "Run your first model" screen will pop up. Simply **click 'Finish'.**
4. Open **RStudio** and go to the **Terminal** window. Type the following to fully install the LLM model:
     ``` zsh
     ollama pull llama3:8b
     ```
5. That's it! Now _Ollama_ can run in the background on your machine, so that the _libbotR_ package can successfully work.

### Ollama Package:
* _ollamar_ is automatically installed when the _libbotR_ package is installed.
  - If you wish to install the _ollamar_ package on its own run the following in RStudio:
     ``` r
     install.packages("ollamar")
     ```

<br>

---

<br>

## Dataset Dependencies

> This package does not include the embedding matrix or LibGuide text. You must load those datasets manually in order to use the functions.
> The datasets can be found in the Google Drive linked below, inside of the `final_data` directory/folder:

-   [Google Drive](https://drive.google.com/drive/folders/1-L87Z91PGjJwp5ZJ2cSX8toZeqUGCiiQ)

*`Data frame with text embeddings (rows = guide sections, cols = vector dimensions)`*

```         
emb_full_libguide_df.rds
```

*`Data frame with full text, titles, URLs, and other metadata`*

```         
text_full_libguide.rds
```

<br>

---

<br>

## Running LibBot on Web Browser:
>To get LibBot working on a localhost web-app (local webpage accessible through your computer), there are two server components that need to be running:

<br>

### Back-end R Server:
>The R server runs the LibBot functions. To get it working do the following:

1. Open **RStudio** and type the following in the console window:
    ``` r
    setwd("/path/2025_startup_libguide_chatbot/libbot_demo/libbotR")
    ```
    >NOTE:
    >Setting the working directory now to make the next step easier. Remember to modify the path so that it correctly leads to `/2025_startup_libguide_chatbot/`.

2. Then load the server by running the _localhost_ script by typing the following in the console:
    ``` r
    source("localhost.R")
    ```
    
    (The R server will start on: <http://127.0.0.1:8000>)

<br>

### Front-end Server (Web UI)
>To get the **UI** for the web-app working, do the following:

1. Still in **RStudio**, go to the **Terminal** window and type the following:
    ``` bash
    cd 2025_startup_libguide_chatbot/libbot_demo/web/
    ```
    >NOTE:
    >Make sure you know where the `/2025_startup_libguide_chatbot/` directory.

2. Now that you've moved into the /web directory, run the following to start up the **UI** server:

    ``` zsh
    python3 -m http.server 1234
    ```
    >NOTE:
    >The '1234' port is arbitrary, so it was chosen for simplicity.
    
5.  #### LibBot is officially up and running!** You can find it on a browser window by typing the following:

    ### <http://127.0.0.1:1234>



<br>


~*A Quarter For Data Science*~

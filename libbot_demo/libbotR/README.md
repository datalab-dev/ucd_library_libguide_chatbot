# libbotR: R Package for UC Davis Library Chatbot

`libbotR` is an R package that helps match user prompts to semantically relevant content using text embeddings and cosine similarity. It was developed as part of a chatbot system for navigating the UC Davis Library Guides.

------------------------------------------------------------------------

## Package Installation

1) Clone/download the `libbotR` repository (or its parent, `startup_libguide_chatbot`) found here:

-   [Github](https://github.com/datalab-dev/2025_startup_libguide_chatbot)

2) Open **RStudio** and type the following in the console window:

``` r
setwd("/path/2025_startup_libguide_chatbot/libbot_demo/libbotR")
```
>NOTE:
>Remember to modify the path so that it correctly leads to `/startup_libguide_chatbot/`:

3) This package was built using the `devtools` package. If you don't have it yet, run the following in the RStudio console:

``` r
install.packages("devtools")
```

4) Finally, to install `libbotR` itself, run the following in the console:

``` r
devtools::install("libbotR")
```

### Loading the package:

>Once the package has been installed, it can be loaded into any R session or script using the following:

``` r
library(libbotR)
```

------------------------------------------------------------------------

## Package Dependencies

| The `libbotR` package **depends** on the `Ollama` [**app**] and `ollamar` [**package**], to work. Here's an explanation for what these two are exactly, where to get them, and how to use them:
<br>

### `Ollama` software vs. the `ollamar` package:

**`Ollama`** = a software/app that can be used as a command-line tool, and as a back-end service for running and managing large language models locally on your machine. _libbot_ uses _Ollama_'s tools to run the library guide search, and also uses _Ollama_'s '**llama3'** LLM model specifically to help with the generative aspect of the chatbot.

**[ INSTALLATION ]**:
1. Download [Ollama](https://ollama.com/) and open it.
2. The "Welcome to Ollama" screen will pop up. Click '**install'** (and input your password if needed)
3. The "Run your first model" screen will pop up. Simply **click 'Finish'.**
4. Open **RStudio** and go to the **Terminal** window. Type the following to fully install the LLM model:
     ``` zsh
     ollama pull llama3:8b
     ```
5. That's it! Now _Ollama_ can run in the background on your machine, so that the _libbotR_ package can successfully work.<br><br><br>

**`ollamar`** = an R package that interfaces with the _Ollama_ software back-end, allowing us to use the language models directly from R—for tasks like the ones needed for the _libbotR_ chatbot (e.g. getting text-embeddings).

**[ INSTALLATION ]**:
1. _ollamar_ is **_automatically_** installed when _libbotR_ is installed (so no need to do it manually).

---
<br>

~*A Quarter For Data Science*~

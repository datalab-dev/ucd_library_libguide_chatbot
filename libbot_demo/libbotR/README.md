# libbotR: R Package for UC Davis Library Chatbot

`libbotR` is an R package that helps match user prompts to semantically relevant content using text embeddings and cosine similarity. It was developed as part of a chatbot system for navigating the UC Davis Library Guides.

------------------------------------------------------------------------

## Package Installation

| 1) Clone/download the `libbotR` repository (or its parent, `startup_libguide_chatbot`) found here:

-   [Github](https://github.com/datalab-dev/2025_startup_libguide_chatbot)

| 2) This package was built using the `devtools` package, which you need to install as well. If you don't have it yet, run:

``` r
install.packages("devtools")
```

| 3) Finally, to install `libbotR` itself, use the following:

Rremember to modify the path so that it correctly leads to `/startup_libguide_chatbot/libbotR`:

``` r
devtools::install("/full/path/to/startup_libguide_chatbot/libbotR")
```

### Loading the package:

``` r
library(libbotR)
```

------------------------------------------------------------------------

## Ollama Installation

| The `libbotR` package and chatbot **depend** on the `Ollama` [**app**]{.underline} and `ollamar` [**package**]{.underline}, to work. Here's an explanation for what these two are exactly, where to get them, and how to use them:

#### `Ollama` software vs. the `ollamar` package:

-   `Ollama` = a software/app that can be used as a command-line tool, and as a back-end service for running and managing large language models locally on your machine.

    `libbot` uses `Ollama`'s tools to run the library guide search, and also uses `Ollama`'s '**llama3'** LLM model specifically to help with the generative aspect of the chatbot.

    -   [INSTALLATION]():
        1.  Download [Ollama](https://ollama.com/) and open it

        2.  A "Welcome to Ollama" screen will pop up. Click '**install'** (and input your password if needed)

        3.  A "Run your first model" screen will pop up. Simply **click 'Finish'.**

        4.  Open **RStudio** and go to the **Terminal** window. Type the following to fully install the LLM model:

            ``` zsh
            ollama pull llama3:8b
            ```

        5.  That's it! Now Ollama can run in the background on your machine, and can therefore be used by the `libbotR` package successfully.

-   `ollamar` = an R package that interfaces with the Ollama software back-end, allowing us to use the language models directly from R—for tasks like the ones needed for the `libbotR` chatbot (e.g. getting text-embeddings).

    -   

        -   `ollamar` is [automatically]{.underline} installed when `libbotR` is installed (so no need to do it manually).

------------------------------------------------------------------------

## Necessary Datasets

| This package does not include the embedding matrix or LibGuide text. You must load those datasets manually in order to use the functions.

| The datasets can be found in the Google Drive linked below, inside of the `final_data` directory/folder:

-   [Google Drive](https://drive.google.com/drive/folders/1-L87Z91PGjJwp5ZJ2cSX8toZeqUGCiiQ)

*`Data frame with text embeddings (rows = guide sections, cols = vector dimensions)`*

```         
emb_full_libguide_df.rds
```

*`Data frame with full text, titles, URLs, and other metadata`*

```         
text_full_libguide.rds
```

~*A Quarter For Data Science*~

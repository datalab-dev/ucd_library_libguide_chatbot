# libbotR

`libbotR` is an R package that helps match user prompts to semantically relevant content using text embeddings and cosine similarity. It was developed as part of a chatbot system for navigating the UC Davis Library Guides.

------------------------------------------------------------------------

## Installation

| 1) Clone/download the `libbotR` repository (or its parent, `startup_libguide_chatbot`) found here:

-   [Github](https://github.com/datalab-dev/2025_startup_libguide_chatbot)

| 2) This package was built using the `devtools` package, which you need to install as well. If you don't have it yet, run:

``` r
install.packages("devtools")
```

| 3) Finally, to install `libbotR` itself, use the following:
| (remember to modify the path so that it correctly leads to `/startup_libguide_chatbot/libbotR`):

``` r
devtools::install("/full/path/to/startup_libguide_chatbot/libbotR")
```

## Loading the package:

``` r
library(libbotR)
```

------------------------------------------------------------------------

## Necessary Datasets and Ollama

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

| Lastly, you will also need to install the `Ollama` app (software used to run LLMs locally), and have it running in the background when using the libbot chatbot or functions. This is where you can find the download:

-   [Ollama](https://ollama.com/)

------------------------------------------------------------------------

**NOTE:**

| Keep in mind that `libbotR` also depends on the `ollamar` R package, which will be installed ***automatically*** upon installation of this package.
| 

#### `Ollama` software vs. the `ollamar` package:

-   `Ollama` = a command-line tool and backend service for running and managing large language models locally on your machine.
-   `ollamar` = R package that interfaces with the Ollama software backend, allowing us to use the language models directly from R—for tasks like the ones needed for the `libbotR` chatbot.

~*A Quarter For Data Science*~

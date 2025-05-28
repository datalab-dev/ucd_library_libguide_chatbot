# libbotR

`libbotR` is an R package that helps match user prompts to semantically relevant content using text embeddings and cosine similarity. It was developed as part of a chatbot system for navigating the UC Davis Library Guides.

------------------------------------------------------------------------

## Installation

| 1) Clone/download the 'libbotR' repository (or its parent, 'startup_libguide_chatbot') found here:

-   [Github](https://github.com/datalab-dev/2025_startup_libguide_chatbot)

| 2) In RStudio, install the package using the following:
| (remember to modify the path so that it correctly leads to */startup_libguide_chatbot/libbotR*):

```         
devtools::install("/full/path/to/libbotR")
```

### Loading the package:

```         
library(libbotR)
```

------------------------------------------------------------------------

## Necessary Datasets

| This package does not include the embedding matrix or LibGuide text. You must load those datasets manually before using the functions.

| The datasets can be found in the Google Drive linked below, inside of the 'final_data' directory/folder:

-   [Google Drive](https://drive.google.com/drive/folders/1-L87Z91PGjJwp5ZJ2cSX8toZeqUGCiiQ)

*`Data frame with text embeddings (rows = guide sections, cols = vector dimensions)`*

```         
emb_full_libguide_df.rds
```

*`Data frame with full text, titles, URLs, and other metadata`*

```         
text_full_libguide.rds
```

------------------------------------------------------------------------

### NOTE:

| Keep in mind that the 'libbotR' package depends on the packages below. They will be installed *automatically* upon installation of this package:

```         
Ollamar
utils
```

~*A Quarter For Data Science*~

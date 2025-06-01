# Library Lib Guide RAG Project

## Project Overview:

This repository contains code for a project to develop a RAG/LLM system using UC Davis Library Lib Guides as the retrieval set for queries based on Ollama. The goal of the project is to create an "Ask a Librarian" chatbot that receives queries (prompts) from users and returns a text response based on a model fine-tuned with the UC Davis Library LibGuides and then, after the text response, includes a links to the most relevant LibGuide webpages based on a RAG system based on cosign similarity of the vector space of the prompt with the vector space of all of the LibGuides.

## Why:

Acknowledging the presence of artificial intelligence in research and academia, our LibBot project aims to transform the pre-existing corpus of UC Davis library guides into a virtual librarian chatbot experience. The LibBot will assist students in research by routing users to the most relevant guides from the library’s vast array of resources.

Links:

-   [Google Drive](https://drive.google.com/drive/folders/1-L87Z91PGjJwp5ZJ2cSX8toZeqUGCiiQ)

Flow Organization: \* [Lucid Chart](https://lucid.app/lucidchart/f6e956d2-5e6b-49f7-a731-82b50d297874/edit?invitationId=inv_9a6fe0aa-a178-4e50-b6e3-1171f8a51155&page=0_0#)

## Project Team Members

-   Lead: Carl Stahmer
-   Lead: Pamela Reynolds
-   Federico Aprile
-   Ayana Carpenter
-   Duong Khuu
-   Yenyun Huang (Sebrina)
-   Phuong Quynh Tran

## Methodologies

1.  Scrape Libguides to generate Corpus
2.  Compute vector embeddings for each document
3.  Compute the embedding of the user prompt, rank guides by cosine similarity, and select the top few relevant guides
4.  Construct a combined prompt of the query and LibGuide text and call LLM
5.  Return generated answer and links for the top LibGuides

## [Getting Started]

> If you wish to use the LibBot tool, you can get started at this user guide: \### [Getting Started with LibBot](https://docs.google.com/document/d/1qWY1o00bZpfU8P-8ocLhzuiji5SjMJv3CaeOmHbE59M/edit?usp=sharing)

------------------------------------------------------------------------

## Necessary R Packages

Web scraping:

``` r
library(xml2)
library(rvest)
library(httr)
```

Data structure and text cleaning:

``` r
library(dplyr)
library(stringr)
library(tidyr)
library(NLP)
library(openNLP)
library(openNLPmodels.en)
library(rJava)
library(jsonlite)
```

Data visualization:

``` r
library(ggplot2)
library(gridExtra)
library(grid)
```

Working with Ollama LLM:

``` r
library(ollamar)
```

Setting up web interface:

``` r
library(servr)
library(httpuv)
```

Finalized custom LibBot package:

``` r
library(libbotR)
```

------------------------------------------------------------------------

## Working with Ollama LLM:

```         
1. Download and install Ollama app
2. Open/launch the Ollama app to start the local server.
3. Install either the stable or latest/development version of ollamar.
```

Install Ollama in R:

``` r
install.packages("ollamar")
```

Getting started example:

```         
library(ollamar)

test_connection()  # test connection to Ollama server
# if you see "Ollama local server not running or wrong server," Ollama app/server isn't running

# download a model
pull("llama3:8b")  # download a model (equivalent bash code: ollama run llama3:8b)

# generate a response/text based on a prompt; returns an httr2 response by default
resp <- generate("llama3:8b", "tell me a 5-word story")
resp

# list available models (models you've pulled/downloaded)
list_models()

   NAME                        ID              SIZE      MODIFIED    
1. llama3:8b                   365c1bd3c000    4.7 GB    2 weeks ago
...
```

------------------------------------------------------------------------

## File and Directory Structure

The basic directory structure for the project is:

``` zsh
2025_startup_libguide_chatbot/
  ├── README.md       # This README.
  ├── libbot_demo
  │   └── libbotR     # Contains custom LibBot R-Package
  │       └── README.md     # Explains how to install and use the package
  │       └── ...
  │   └── web         # Contains LibBot web-page architecture
  │       └── README.md     # Explains how to get LibBot web-page working and running
  │       └── ...
  │
  └── src             # Contains ALL of the R/Python source code 
      └── ...
```

### src/ Contents

```         
 
 └── src             # Contains ALL of the R/Python source code 
      ├── python
      │   ├── Finetuning_Unsloth.ipynb    # Discontinued model fine-tuning
      │   ├── librarian.txt               # Discontinued model context
      │   ├── ollama_chat.py              # Discontinued model interactive chat setup
      │   └── ollama_testing.py           # Discontinued model interactive chat test
      |
      |
      └── r           # R-scripts with functions
          ├── get_sub_pages.R         # idea to get Libguide sub-pages URLs
          ├── scrape_lib_guides.R     # scrape lib-guide pages for html/xml content
          ├── get_html.R              # get proper part of html/xml content
          ├── appending_sub_pages.R   # add sub-pages of LibGuides as new rows
          ├── unique_url_checker.R    # checking uniqueness of sub-pages
          ├── recursion.R             # applying functions above to all rows
          ├── xml_to_text.R           # xml/html content to text
          ├── make_relationship_df.R  # relational df connecting main libguides to              |                             their sub-pages
          ├── scrape_title.R          # get title of pages
          ├── stats_data_viz.R        # first visual and stats on pages
          ├── text_chunks.R           # testing for extracting titles, text, URLs
          ├── v1_text_chunks.R        # finalizing df with cleaned data
          |                           # extracted titles, text, URLs
          ├── ollamar.R               # testing basic chatbot interface in R
          ├── prepare_texts_for_analysis.R    # build two corpus dfs merging titles
          |                                     and content into structured text:
          |                                    -one for sub-page level
          |                                    -one for full libguide pages
          ├── vector_space.R          # testing getting vector space of corpus
          |
          ├── sentence_grouping_for_large_chunks.R    # testing splitting text chunks           |                                             chunks into sentences for               |                                             formatting and vector space
          |
          ├── paste_small_sections.R                  # handling small text chunks
          ├── split_chunk_sentences.R                 # finalized sentence splitting
          ├── unnested_vector.R                       # testing for eventual unnesting           |                                             of vector space store
          ├── v2_corpus_stats.R       # stats on new corpus
          ├── sentence_grouping.R     # finalized grouping of sentences into chunks 
          |                             to handle size issues
          ├── vector_space_functions.R                # first successful iteration of
          |                                             functions used to run libguide
          |                                             search
          ├── get_top_unnested.R      # second iteration of functions used to run               |                             libguide search; on unnested vector space;
          |                             creation of final vector space df
          |                             (emb_full_libguide.RDS)
          |
          ├── pasted_sentence_groups.R  # cleaning data to create final corpus df
          |                               (text_full_libguide.RDS)
          |
          |
          └── final_demo_script.R       # final script for demo; was used to build
                                          LibBot R package
```

### Outputs

```         
file_a.rds         description
file_b.rds         description
```

------------------------------------------------------------------------

| STS 195: Research in Data Studies, Spring 2025 Outputs and Workflow by Week

![LibBot (2)](https://github.com/user-attachments/assets/17a63997-5e89-43f8-91d6-3f11add5983e)

~*A Quarter For Data Science*~

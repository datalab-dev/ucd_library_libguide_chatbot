# Expansion of LibBot: Library Guide RAG Project

> [!IMPORTANT]  
> - This project originated as a group collaboration back during 2025 Spring Quarter. The original team version, team member agknowledgements, resources and data store, and documentation can be found in the $\color{Purple}\large{\textsf{STS195-legacy-group-original}}$ branch.
> - LibBot currently works with libguides based on a final scrape conducted on February 20th, 2025. The additional library data that has been updated since then will be incorporated in the next iterations of LibBot.

## Project Overview:

This repository contains code for LibBot, a virtual librarian chatbot, that was developed to retrieve and synthesize UC Davis Library resources to connect researchers with relevant materials and librarians.

The project involved systematized data scraping, preprocessing, cleaning, and organization to feed into embedding and retrieval systems using Retrieval-Augmented Generation (RAG) paired with large language model responses.

Various Sentence-Transformer embedding models were researched and analyzed through documentation to balance efficiency, speed, and quality. A Python/PyTorch pipeline was built with optimized pooling strategies and prompt engineering.

LibBot currently retrieves resources based on queries and provides citations linking to library materials. Synthesis capabilities for user accessibility are being implemented alongside a transition to server-based architecture for the deployable prototype. 


## Why:

Acknowledging the presence of artificial intelligence in research and academia, LibBot aims to provide consistent access to library expertise while unifying scattered resources into a singular academic research ecosystem, maintaining quality research support despite institutional constraints (reduced librarian availability and funding). Transforming the pre-existing corpus of UC Davis library guides and resources into a virtual librarian chatbot experience, this system will assist researchers by routing them to the most relevant library resources.

## Current Project Version Team Members

-   Lead: Carl Stahmer
-   Federico Aprile

## Methodologies

1.  Scrape Libguides to generate Corpus
2.  Compute vector embeddings for each document
3.  Compute the embedding of the user prompt, rank guides by cosine similarity, and select the top few relevant guides
4.  Construct a combined prompt of the query and LibGuide text and call LLM
5.  Return generated answer and links for the top LibGuides

## Getting Started

### If you wish to use the LibBot** tool, you can get started with this user guide: [Getting Started with LibBot](https://docs.google.com/document/d/1qWY1o00bZpfU8P-8ocLhzuiji5SjMJv3CaeOmHbE59M/edit?usp=sharing)

> Note: The LibBot is trained on UC Davis Library Guides and works with Ollama to produce an AI-Generated summary. As with all large language model output, use your own critical reading and thinking skills to assess the validity and reliability of this response for your specific query.

<br>

------------------------------------------------------------------------

<br>

## Necessary R Packages

Finalized custom LibBot package:

#### [[INSTALLATION](https://github.com/datalab-dev/2025_startup_libguide_chatbot/tree/main/libbot_demo/libbotR#readme)]

``` r
library(libbotR)
```

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

Working with Ollamar:

``` r
library(ollamar)
```

Setting up web interface:

``` r
library(servr)
library(httpuv)
```

<br>

------------------------------------------------------------------------

<br>

## Working with Ollama LLM:

**Ollama App**
* Download [Ollama](https://ollama.com/) and run it.

**Ollama in R**
* _ollamar_ is automatically installed when the _libbotR_ package is installed.
  - If you wish to install the _ollamar_ package on its own run the following in RStudio:
     ``` r
     install.packages("ollamar")
     ```


Example of Ollama Usage in R:

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
1. llama3:8b         365c1bd3c000            4.7 GB   2 weeks ago
...
```

<br>

------------------------------------------------------------------------

<br>

## GitHub File and Directory Structure

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

<br>

---

<br>

## Google Drive Data Output Structure:

>All of the datasets and outputs from this project, and their corresponding metadata, have been recorded in this Data Dictionary:
#### [[Data Dictionary](https://docs.google.com/spreadsheets/d/1exjwKkVhQZlc18X9N3xGJDGEbcCvTbJCSRaJqXYWKn0/edit?usp=sharing)] 
#### [[Google Drive](https://drive.google.com/drive/folders/1-L87Z91PGjJwp5ZJ2cSX8toZeqUGCiiQ)]

<br>

---

<br>

## STS 195: Research in Data Studies, Spring 2025 Outputs and Workflow by Week

![LibBot (2)](https://github.com/user-attachments/assets/17a63997-5e89-43f8-91d6-3f11add5983e)

~*A Quarter For Data Science*~

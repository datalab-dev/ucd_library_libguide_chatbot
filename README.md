# Library Lib Guide RAG Project
## Project Overview:
This repository contains code for a project to develop a RAG/LLM system using UC Davis Library Lib Guides as the retreival set for queries based on Ollama.   The goal of the project is to create an "Ask a Librarian" chatbot that receives queries (prompts) from users and returns a text response based on a model finetuned with the UC Davis Library LibGuides and then, after the text response, includes a links to the most relevant LibGuide webpages based on a RAG system based on cosign similarity of the vector space of the prompt with the vector space of all of the LibGuides.

## Why:
Acknowledging the presence of artificial intelligence in research and academia, our LibBot project aims to transform the pre-existing corpus of UC Davis library guides into a virtual librarian chatbot experience. The LibBot will assist students in research by routing users to the most relevant guides from the library’s vast array of resources. 

Links:

* [Google Drive](https://drive.google.com/drive/folders/1-L87Z91PGjJwp5ZJ2cSX8toZeqUGCiiQ)

Flow Organization:
* [Lucid Chart](https://lucid.app/lucidchart/f6e956d2-5e6b-49f7-a731-82b50d297874/edit?invitationId=inv_9a6fe0aa-a178-4e50-b6e3-1171f8a51155&page=0_0#)

## Project Team Members
* Lead:  Carl Stahmer
* Lead:  Pamela Reynolds
* Federico Aprile
* Ayana Carpenter
* Duong Khuu
* Yenyun Huang (Sebrina)
* Phuong Quynh Tran

## Methodologies
1. Scrape Libguides to generate Corpus
2. Compute vector embeddings for each document
3. Compute the embedding of the user prompt, rank guides by cosine similarity, and select the top few relevant guides
4. Construct a combined prompt of the query and LibGuide text and call LLM
5. Return generated answer and links for the top LibGuides


## Getting Started
To get started, you will need this user guide: 
### [Getting Started with LibBot](https://docs.google.com/document/d/1qWY1o00bZpfU8P-8ocLhzuiji5SjMJv3CaeOmHbE59M/edit?usp=sharing)

## Necessary R Packages

Web scraping:
```
library(xml2)
library(rvest)
library(httr)
```
Data structure and text cleaning:
```
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
```
library(ggplot2)
library(gridExtra)
library(grid)
```
Working with Ollama LLM: 
```
library(ollamar)
```
Setting up web interface:
```
library(servr)
library(httpuv)
```

## Working with Ollama LLM:
```
1. Download and install Ollama app
2. Open/launch the Ollama app to start the local server.
3. Install either the stable or latest/development version of ollamar.
```
Install Ollama in R:
```
install.packages("ollamar")
```

Getting started:
```
library(ollamar)

test_connection()  # test connection to Ollama server
# if you see "Ollama local server not running or wrong server," Ollama app/server isn't running

# download a model
pull("llama3.1")  # download a model (equivalent bash code: ollama run llama3.1)

# generate a response/text based on a prompt; returns an httr2 response by default
resp <- generate("llama3.1", "tell me a 5-word story")
resp

# list available models (models you've pulled/downloaded)
list_models()
                        name    size parameter_size quantization_level            modified
1               codegemma:7b    5 GB             9B               Q4_0 2024-07-27T23:44:10
2            llama3.1:latest  4.7 GB           8.0B               Q4_0 2024-07-31T07:44:33

```

## File and Directory Structure

The directory structure for the project is:

```
data/           Input and Output Data sets (in .gitignore)
docs/           Supporting documents
models/         Trained and serialized models
notebooks/      Jupyter notebook source files
src/r           R source code
src/py          Python source code
README.md       This file
```

### src/r Contents
```
appending_sub_pages.R                function to add sublinks of a page in a new row
get_html.R                           function to get html content of a page
get_sub_pages.R
localhost.R
make_relationship_df.R               script to make a relationship dataframe with the parent and child ids
ollama.R                             initial ollama testing using R with basic terminal chatbot
paste_small_sections.R
pasted_sentence_groups.R
prepare_texts_for_analysis.R         contains the data cleaning tasks to create initial corpuses
recursion.R
scrape_lib_guides.R          
scrape_title.R
sentence_grouping.R
sentence_grouping_for_large_chunks.R script to group large text chunks
split_chunk_sentences.R              script to break chunks into sentences  
stats_data_viz.R
text_chunks.R
unique_url_checker.R
unnested_vector.R
v2_corpus_stats.R                    calculating statistics of corpus sections' word/sentence counts.
vector_space.R
vector_space_functions.R
xml_to_text.R
     
```

### src/python Contents
```
ollama_chat.py          initial ollama testing using python with UI chatbot
ollama_testing.py       initial ollama testing using python with terminal chatbot  
```

### Outputs
```
file_a.rds         description
file_b.rds         description
```

A more thorough overview of outputs in a week-by-week format 
## STS 195: Research in Data Studies, Spring 2025 Outputs and Workflow by Week

![LucidChart](https://pdf-service-lucidchart-com.s3.amazonaws.com/355939a8-35cf-4983-bd97-11083e69c8e8?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEOr%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJHMEUCIHurXnRy4z5WH%2Bm5S5qSAidQQtk7c%2F%2FSJsdeQpmWCFcVAiEAxJGWRYNQmpLrhiV9t2iL9akiQv48ij0ICGxkYAdZcGcquQUIs%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw5MzU2MDY5MjYxODIiDIBb9qEYRNp7a9LywiqNBb%2BCu%2F8Dyuaab20HycXpoC2j2WJp%2BpnKkNObXgoIhncsc%2FFn6OUUmZxMZZuDa%2B8vCy4kCtJyTfFVWBsF%2BFFx6lOzN7BPrh1295c2EvXXfKVOG98mGpz2G%2FFPTgtBn2lkhxBt7IQX3uqsDTy4%2FHd%2BoPd50zmPXRheukzNmUo0B9YnvQbvmn%2BWMrPDAXAn%2FAqUba7goaky0RhmXOUmHN6w%2FCwnrp5zbNpJfN9sCMZZHkXh17qU%2FI84A5nzRHFQ9al06OSgPJOUnKlnkGvD3ezHAyhIscbgVlcpSGn1A17DmJ0srMWB3moYKgW7iX8TsHwbbz2EFxRVjnpLDovrhiGuSDhkYFX6VvmYva7cu1lwBOlx54DnDhNqVokNVPIKKfXqCCVUudpTeyqNhAVe12WGaZiMynaUZevJ1CNdxC8WY8p9FiYzqCfo94HoH88OOS7iQlkxi2udU3aN%2F%2F34ntvOxZj6zVfAERmADPiECIg4qbcNisnpnmyV%2Bn57LIdpiKhlfWRPqluxKpHMqE9yxNQLSn1HcnHFh5N0TMbXFfDA%2Bl%2F0dY%2Bq1JcXbA6uJ4xP%2BXp2z%2B4HjildFgFqnjfvR%2FJhoJshrQBvuA5FnykwPeo8zpPxuhqgLFx3%2FTbX6rJ%2FJsrlcOqUt8GbMJeGiHKzsNdeij65HyZXsY89ijPokKmVXsvK5iubUr0ZLCjYVJKOGcIsh3eSP2vh5askER5W4w6Ne%2BzUOqf0xzRA8uA87ZZNcqZineFjX4qXz1zO8r1U922UHubR2BoDsTzhkYDFkObZHr54YpVkg3uTbRUD3ioR5hcEWDSyRmOk5bgvk6eOnOmipsLoMjAF5M%2Fh2NVDnBkx2UdLTPGwbJu5gYQwbdPdMKe26cEGOrEB3QEUTEbIKJ49RE8h5y1CQ4K9SbzDJzGiySxiOJHwpRHISUAiKWP83tN0ezgArTueTGoBt1l0eje7SvmYkHEW8weVrKlmIPH6lG88nHAaVMzK6ugys2%2BVTPWlDaIaPjPfD%2BctVY1r66nXtZOozqQBWFet7RB7NuglV71a4I7FxK8dfofUVB0fp8dj6qUkvdmbi1S7o5c8qZbEe2UkKMVk7dmAqDzp1rFbswoCR8yZKUmr&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20250531T025502Z&X-Amz-SignedHeaders=host&X-Amz-Expires=86399&X-Amz-Credential=ASIA5TVUEXNTK242MVJH%2F20250531%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=dce29867ab6dd9abe249abb6a25aa6b1374442aa8edf32425c7c4fed2721da61)


![LibBot (2)](https://github.com/user-attachments/assets/17a63997-5e89-43f8-91d6-3f11add5983e)


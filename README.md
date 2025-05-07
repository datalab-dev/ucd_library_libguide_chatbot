# Library Lib Guide RAG Project
## Project Overview:
This repository contains code for a project to develop a RAG/LLM system using UC Davis Library Lib Guides as the retreival set for queries based on Ollama.   The goal of the project is to create an "Ask a Librarian" chatbot that receives queries (prompts) from users and returns a text response based on a model finetuned with the UC Davis Library LibGuides and then, after the text response, includes a links to the most relevant LibGuide webpages based on a RAG system based on cosign similarity of the vector space of the prompt with the vector space of all of the LibGuides.

## Why:

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
appending_sub_pages.R           function to add sublinks of a page in a new row
cosine_similarity.R           function to find cosine similarity between words
get_html.R           function to get html content of a page
get_sub_pages.R      
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
```
Data visualization:
```
library(ggplot2)
library(gridExtra)
library(grid)
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

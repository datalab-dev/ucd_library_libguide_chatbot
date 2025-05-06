# Library Lib Guide RAG Project

This repository contains code for a project to develop a RAG/LLM system using UC Davis Library Lib Guides as the retreival set for queries based on Ollama.   The goal of the project is to create an "Ask a Librarian" chatbot that receives queries (prompts) from users and returns a text response based on a model finetuned with the UC Davis Library LibGuides and then, after the text response, includes a links to the most relevant LibGuide webpages based on a RAG system based on cosign similarity of the vector space of the prompt with the vector space of all of the LibGuides.

Links:

* [Google Drive](https://drive.google.com/drive/folders/1-L87Z91PGjJwp5ZJ2cSX8toZeqUGCiiQ)

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
file_a.R           description
file_b.R           description
```

### src/python Contents
```
file_a.py          description
file_b.py          description
```

### Outputs
```
file_a.rds         description
file_b.rds         description
```


## Project Team Members
* Lead:  Carl Stahmer
* Lead:  Pamela Reynolds
* Federico Aprile
* Ayana Carpenter
* Duong Khuu
* Yenyun Huang (Sebrina)
* Phuong Quynh Tran

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

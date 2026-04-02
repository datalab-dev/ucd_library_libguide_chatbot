# Expansion of LibBot: Library Guide RAG Project

> [!IMPORTANT]  
> - This project originated as a group collaboration back during 2025 Spring Quarter. The original team version (mainly built in R), team member agknowledgements, resources and data store, and documentation can be found in the $\color{Purple}\large{\textsf{STS195-legacy-group-original}}$ branch.
> - LibBot currently works with libguides based on a final scrape conducted on February 20th, 2025. The additional library data that has been updated since then will be incorporated in the next iterations of LibBot.

## Current Contributors

-   **Project Lead**: DataLab Director Dr. Carl Stahmer
-   **Lead Developer & Mantainer**: Federico Aprile

---

## Project Overview:

**LibBot** is a virtual librarian chatbot designed to unify scattered academic resources into a singular research ecosystem. Developed to support the UC Davis Library, it connects researchers with relevant materials and expertise, maintaining high-quality research support even amidst institutional constraints like reduced librarian availability.

### Technical Implementation

The system transforms the UC Davis library’s corpus of guides and resources into a conversational experience through a structured RAG (Retrieval-Augmented Generation) pipeline:

- **Data Ingestion & Cleaning**: Systematized scraping and preprocessing of heterogeneous library data to ensure a clean, searchable corpus.
- **Semantic Representation**: Utilization of Sentence-Transformer models to generate high-quality vector embeddings for documents and queries. These models were benchmarked to balance computational efficiency on CPU-only environments with retrieval accuracy.
- **Retrieval & Context Selection**: A Python/PyTorch-based retrieval engine that uses optimized pooling strategies to identify and rank the most relevant document chunks based on user queries, using cosine similarity.
- **Retrieval-Augmented Generation (RAG)**: A prompt engineering layer that synthesizes the retrieved context and passes it to a Large Language Model (LLM) to generate natural, cited responses and links.

### Current Capabilities & Roadmap

LibBot currently retrieves resources based on natural language queries and provides direct citations to library materials. Development is currently focused on:
- **Synthesis & Accessibility**: Enhancing the model's ability to summarize complex information for better user experience.
- **Deployment**: Transitioning to a server-based architecture for a fully deployable prototype.

---

# Getting Started


> [!TIP]  
> ### If you wish to use and interact with LibBot:
> 1. Connect to the UC Davis Library VPN
> 2. Go to http://server-hostname:8075 (replace temporary name with actual server name)

> [!NOTE]
> As with all large language model output, use your own critical reading and thinking skills to assess the validity and reliability of this response for your specific query.

<br>

------------------------------------------------------------------------

## Project Dependencies:

------------------------------------------------------------------------

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

# LibBot

A semantic search chatbot for the UC Davis Library. LibBot lets users ask natural language questions and get back relevant resources from the library's LibGuides corpus, grounded by an LLM-generated summary. Built with FastAPI, ChromaDB, Qwen3-Embedding, and Ollama. Accessible to anyone on the UC Davis Library VPN. Newest iteration of LibBot, transitioned from the R-based prototype and Ollama structure, to Python and its transformers and transformer-adjacent libraries. 

---

## Structure
```
libbot_bert/
├── libbot_pkg/        # Libbot package, with search/retrieval functionality, connection to vector database, and FastAPI for web server and interface
├── research/           # Benchmarking various embedding models, retrieval methods, visualizations, and database structures.
├── pixi.toml          # Environment and dependency definitions
├── pixi.lock          # Freezes exact versions of all project dependencies—including transitive ones—that are installed (for reproducibility/safety)
├── .gitignore/.gitattributes          # What files Git should not track, and how Git should handle the files it does track
└── test_retriever.py   # Testing whether libbot_pkg module imports work on a simple script
```


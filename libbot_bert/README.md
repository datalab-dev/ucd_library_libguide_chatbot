# [Libbot_Bert]

Newest iteration of Libbot, transitioned from the R-based prototype and Ollama structure, to Python and its transformers and transformer-adjacent libraries. 

## Structure
```
libbot_bert/
├── libbot_pkg/        # Libbot package, with search/retrieval functionality, connection to vector database, and FastAPI for web server and interface
├── scripts/           # Testing out different embedding models, search scripts, visualizations, and database structures.
├── pixi.toml          # Environment and dependency definitions
├── pixi.lock          # Freezes exact versions of all project dependencies—including transitive ones—that are installed (for reproducibility/safety)
├── .gitignore/.gitattributes          # What files Git should not track, and how Git should handle the files it does track
└── test_retriever.py   # Testing whether libbot_pkg module imports work on a simple script
```

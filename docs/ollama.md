# Ollama LLM Configuration

LibBot uses Ollama to serve the LLM responsible for synthesizing retrieved library documents into a natural language response. This document covers the Modelfile system used to configure and register models on the datasci server, the parameter choices made for this deployment, and the two models currently evaluated for LibBot.

<br>

---

## Modelfiles

The `models/` directory in the project root contains Ollama Modelfiles for each LLM evaluated for LibBot. A Modelfile is a configuration manifest that Ollama reads once during model registration to bake specific parameters and a system prompt into a named local model instance. This makes model behavior reproducible across server restarts and team members without requiring runtime configuration.

``` bash
libbot/
├── models/
│   ├── Modelfile.gemma12b   # Gemma 3 12B QAT — high accuracy
│   └── Modelfile.gemma3n    # Gemma 3n E4B — high speed
├── libbot_pkg/
└── ...
```

> [!NOTE]
> Modelfiles are not referenced by the Python application at runtime. They are used
> once during model registration and serve as the reproducible recipe for model
> behavior on the server.

---

### Registering a Model

To register or update a model after modifying a Modelfile:

```bash
ollama create <model-name> -f models/<Modelfile>
```

For example:
```bash
ollama create libbot-scholar -f models/Modelfile.gemma12b
```

Once created, update `OLLAMA_MODEL` in the project's `.env` file to the chosen model name so LibBot uses it at runtime.


<br>

---

## Model Blueprint and Customization

**`num_ctx` (4096):** Provides enough context window for the user query, 3–4 retrieved document chunks, and conversation history, without incurring the exponential CPU prefill cost of larger windows.

**`temperature` (0.3):** A low temperature keeps the model focused on the retrieved library content and reduces the tendency to drift toward plausible-sounding but unsupported claims — important for a tool whose purpose is to surface accurate library resources.

**`min_p` (0.1):** The primary sampling filter. Removes tokens with a probability lower than 10% of the most likely token at each step.

**`top_p` (1.0):** Explicitly disabled by setting to 1.0, allowing `min_p` to handle nucleus sampling alone.

**`top_k` (40):** Limits the initial token vocabulary pool at each step, preventing the model from considering low-probability tokens that are unlikely to be relevant in a technical library context.

**`system prompt`:** Ollama allows a system-prompt definition in the Modelfile (or via API), which is a foundational hidden **instruction set** that dictates an LLM's persona, behavior, constraints, and output format before it processes any user input. It prepends context, ensuring the model acts as a specific persona (e.g., "you are a helpful coder") rather than a generic chatbot.


<br>

---
### Tested Models

**Gemma 3 12B QAT** (`Modelfile.gemma12b`) &rarr; saved as `libbot_gemma3-12b`
> The higher-accuracy option. Uses the QAT (Quantization-Aware Training) variant of Gemma 3 12B, sourced from `hf.co/unsloth/gemma-3-12b-it-qat-GGUF:Q4_0`. Unlike standard GGUF quantization, QAT was trained specifically to maintain near 16-bit accuracy while running at 4-bit speeds — making it well suited for a RAG context where faithfulness to retrieved documents matters.

**Gemma 3n E4B** (`Modelfile.gemma3n`) &rarr; saved as `libbot_gemma3n-4b`
> The higher-speed option. Uses Gemma 3n's MatFormer architecture, which allows high-speed CPU inference by effectively operating as a 4B model while retaining the organizational structure of a larger system. 

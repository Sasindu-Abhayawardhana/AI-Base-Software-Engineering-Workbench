# AI-Powered Software Engineering Workbench

An interactive Streamlit workbench for turning software requirements into architecture insights, diagrams, and implementation guidance using AI models.

## Overview

This repository provides two Streamlit-based workbench experiences:

- `workbench.py`: a software engineering assistant workflow.
- `rag_workbench.py`: an architecture-focused workbench with Retrieval-Augmented Generation (RAG) support using local course materials.

The apps are designed to help with:

- Requirement analysis
- Architecture style recommendation
- Component and technology suggestions
- Mermaid-based architecture diagram generation
- Risk and quality attribute reasoning

## Features

- Modern Streamlit UI with structured analysis panels
- Support for local LLM usage via Ollama
- Optional multi-provider model selection UI (e.g., OpenAI, Claude, Gemini, DeepSeek in `rag_workbench.py`)
- RAG flow over local documents in `course_materials/`
- Mermaid diagram rendering inside the app

## Project Structure

```text
Software_WorkBench/
├── rag_workbench.py        # Main architecture + RAG Streamlit app
├── workbench.py            # Streamlit software engineering workbench
├── prompts.py              # Prompt templates used by analysis flows
├── course_materials/       # Local source docs for RAG ingestion
├── chroma_db/              # Local Chroma vector database storage
├── requirements.txt        # Python dependencies (currently minimal/empty)
└── README.md
```

## Prerequisites

- Python 3.10+
- `pip`
- [Ollama](https://ollama.com/) running locally (for local model flows)

Recommended Ollama models used in this repo:

- `mistral` (generation)
- `nomic-embed-text` (embeddings)
- `llama3` (used by `workbench.py`)

## Installation

1. Clone the repository:

   ```powershell
   git clone <your-repo-url>
   cd Software_WorkBench
   ```

2. Create and activate a virtual environment:

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

4. Ensure Ollama is running and pull required models:

   ```powershell
   ollama pull mistral
   ollama pull nomic-embed-text
   ollama pull llama3
   ```

## Running the Apps

Run the architecture + RAG workbench:

```powershell
streamlit run rag_workbench.py
```

Run the alternate workbench UI:

```powershell
streamlit run workbench.py
```

After startup, open the local URL shown by Streamlit (typically `http://localhost:8501`).

## RAG Data Notes

- Place source PDF/material files in `course_materials/`.
- Vector index data is stored in `chroma_db/`.
- If you change source materials heavily, re-indexing may be needed (depends on your app flow/session).

## Configuration Notes

- `workbench.py` uses `OLLAMA_URL = http://localhost:11434/api/generate` and `MODEL_NAME = llama3`.
- `rag_workbench.py` defaults include:
  - generation model: `mistral`
  - embeddings model: `nomic-embed-text`
  - materials directory: `course_materials`
  - vector store directory: `./chroma_db`

If you plan to use hosted providers shown in the UI, configure the required API keys in your local environment before running.

## Troubleshooting

- **`Connection refused` or model errors**: verify Ollama is running and models are pulled.
- **Missing package errors**: reinstall dependencies with `pip install -r requirements.txt`.
- **No RAG results**: confirm files exist in `course_materials/` and index creation completed.
- **Port already in use**: run Streamlit on another port, e.g. `streamlit run rag_workbench.py --server.port 8502`.

## License

See `LICENSE` for license information.
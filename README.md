# AI-Base Software Engineering Workbench

### Intelligent Architecture Recommendation Assistant

An AI-powered software engineering workbench built with `Streamlit`.

The app takes high-level software requirements and generates:
- recommended architecture style,
- architectural rationale,
- quality/security/scalability tactics,
- component and tech-stack suggestions,
- Mermaid diagram code and visual output.

It supports both local and hosted LLM providers and uses optional RAG (Retrieval-Augmented Generation) with a Chroma vector store.

## Features

- Streamlit web interface with light/dark theme support
- Model selection via dropdown (`Local`, `Gemini`, `Claude`, `DeepSeek`, `OpenAI`)
- API key input for hosted providers
- RAG pipeline using course/project documents from `course_materials/`
- Structured JSON-based architecture output
- Mermaid diagram rendering + direct link to Mermaid Live Editor

## Project Structure

```text
.
├── rag_workbench.py      # Main RAG-enabled workbench app
├── workbench.py          # Alternative/legacy app variant
├── prompts.py            # Prompt helpers (if used)
├── requirements.txt      # Python dependencies
├── course_materials/     # Input docs for retrieval context
└── chroma_db/            # Local persisted vector store
```

## Requirements

- Python 3.10+
- (Optional for local model) [Ollama](https://ollama.com/) running on `http://localhost:11434`
- API key for cloud providers (`Gemini` / `Claude` / `DeepSeek` / `OpenAI`)

## Installation

1. Clone or download this repository.
2. Create and activate a virtual environment.
3. Install dependencies:

```powershell
pip install -r requirements.txt
```

## Run the App

Main app:

```powershell
streamlit run rag_workbench.py
```

Alternative app:

```powershell
streamlit run workbench.py
```

Then open the local URL shown in terminal (usually `http://localhost:8501`).

## How to Use

1. Select a model from the **Model** dropdown.
2. Enter API key (required for non-local providers).
3. Enter high-level system requirements.
4. Click **Generate**.
5. Review architecture recommendation, rationale, tactics, and Mermaid diagram.
6. Use **Open in Mermaid Live** for external editing/export.

## RAG Knowledge Base

- Put your source documents in `course_materials/`.
- On app startup, documents are chunked and embedded.
- Chunks are stored/reused in `chroma_db/`.

If the knowledge base is empty or dependencies are missing, the app still runs with reduced RAG capabilities.

## Supported Providers

- Local (Ollama): `mistral`
- Gemini: `gemini-2.0-flash`, `gemini-1.5-flash`, `gemini-1.5-pro`
- Claude: `claude-3-5-haiku-20241022`, `claude-3-5-sonnet-20241022`, `claude-3-opus-20240229`
- DeepSeek: `deepseek-chat`, `deepseek-reasoner`
- OpenAI: `gpt-4o-mini`, `gpt-4o`, `gpt-4-turbo`

## Notes

- Keep API keys secure and do not hardcode them in source files.
- For local usage, ensure Ollama server is running and the selected model is pulled.
- Mermaid rendering depends on valid Mermaid syntax returned by the model.

## License

Use for educational/research purposes unless you add your own project license.
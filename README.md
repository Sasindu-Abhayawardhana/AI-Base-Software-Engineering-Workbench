# AI-Powered Software Engineering Workbench

**From requirements to architecture — instantly.**

A professional, high-fidelity engineering workbench built with Streamlit for turning high-level software requirements into structured architectural designs, technical stacks, and interactive diagrams using Retrieval-Augmented Generation (RAG).

## 🚀 Key Features

- **Professional Design System**: Theme-aware interface with instant Light/Dark mode toggling and a clean industrial aesthetic.
- **Unified Streaming Engine**: Native support for token-by-token generation across multiple providers:
  - **Local**: Ollama (Mistral/Llama3)
  - **Cloud**: Google Gemini, Anthropic Claude, DeepSeek, and OpenAI.
- **Intelligent RAG Grounding**: Deep retrieval layer that contextualizes AI responses using local documentation in `course_materials/`.
- **Architectural Suite**:
  - Pattern recommendation and justification.
  - Tactic analysis (Scalability, Availability, Security).
  - Technology stack mapping and component breakdowns.
  - Risk assessment and quality attribute reasoning.
- **Dynamic Visualization**: Integrated Mermaid.js rendering with a direct "Live Editor" export for professional editing.

## 📁 Project Structure

```text
Software_WorkBench/
├── rag_workbench.py        # Main workbench with RAG and Professional UI
├── workbench.py            # Legacy software engineering assistant
├── prompts.py              # prompt templates for analysis flows
├── course_materials/       # Document repository for RAG ingestion
├── chroma_db/              # Persistent vector store storage
├── requirements.txt        # Python dependency manifest
└── README.md
```

## 🛠️ Prerequisites

- **Python**: 3.10 or higher.
- **Ollama**: Required for local model execution and embeddings.
- **Models**:
  - `ollama pull mistral` (Primary local model)
  - `ollama pull nomic-embed-text` (Required for RAG)

## 📥 Installation

1. **Clone and Navigate**:
   ```powershell
   git clone <your-repo-url>
   cd Software_WorkBench
   ```

2. **Virtual Environment**:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

## 🖥️ Usage

Launch the primary workbench:
```powershell
streamlit run rag_workbench.py
```

### RAG Setup
1. Place architectural documents (PDF, TXT, MD) into the `course_materials/` directory.
2. The app will automatically build or load the vector index into `chroma_db/` upon startup.
3. Status indicators in the UI will confirm when the "Knowledge Base" is ready.

## ⚙️ Configuration

- **API Keys**: For Gemini, Claude, or OpenAI, keys are held in session memory only—never persisted to disk.
- **Embedding Configuration**: Defaulted to `nomic-embed-text` via Ollama for high-performance local vectorization.

## 🤝 Contributing

Contributions to prompt templates or UI components are welcome. Please ensure any changes to `rag_workbench.py` maintain theme compatibility and CSS isolation.

---
*Developed for AI-powered software design automation.*
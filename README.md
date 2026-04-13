# Financial Doc Chatbot

[![CI](https://github.com/JRA-CodingLab/financial-doc-chatbot/actions/workflows/ci.yml/badge.svg)](https://github.com/JRA-CodingLab/financial-doc-chatbot/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)

A RAG-powered chatbot for financial document question-answering. Upload PDFs (annual reports, balance sheets, income statements), ask questions in natural language, and get answers grounded in your documents — with source citations.

## Features

- **PDF Ingestion** — Upload financial documents through the web UI or API.
- **Conversational Q&A** — Ask follow-up questions with full conversation memory.
- **Source Citations** — Every answer includes references to the source documents.
- **Vector Search** — ChromaDB stores document embeddings for fast semantic retrieval.
- **Clean Architecture** — FastAPI backend + Streamlit frontend, cleanly separated.

## Architecture

```
┌──────────────┐     HTTP     ┌──────────────────┐     LangChain     ┌──────────┐
│   Streamlit  │ ──────────── │   FastAPI Server  │ ────────────────  │ ChromaDB │
│   Chat UI    │              │   /upload  /query │                   │  Vectors │
└──────────────┘              └──────────────────┘                   └──────────┘
                                       │
                                       ▼
                              ┌──────────────────┐
                              │   OpenAI GPT API  │
                              └──────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.10+
- An [OpenAI API key](https://platform.openai.com/api-keys)

### Installation

```bash
git clone https://github.com/JRA-CodingLab/financial-doc-chatbot.git
cd financial-doc-chatbot

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

### Configuration

```bash
cp .env.example .env
# Edit .env and set your OPENAI_API_KEY
```

### Run the Backend

```bash
uvicorn backend.server:app --reload
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### Run the Frontend

```bash
streamlit run frontend/chat_ui.py
```

Opens in your browser at `http://localhost:8501`.

## API Endpoints

| Method | Path       | Description                           |
|--------|------------|---------------------------------------|
| POST   | `/upload/` | Upload a PDF for ingestion            |
| GET    | `/query/`  | Ask a question (`?q=your question`)   |

### Example

```bash
# Upload a PDF
curl -X POST http://localhost:8000/upload/ \
  -F "file=@annual_report_2024.pdf"

# Ask a question
curl "http://localhost:8000/query/?q=What%20was%20the%20total%20revenue?"
```

## Testing

```bash
pytest
```

All tests mock external services — no API keys required.

## Tech Stack

| Component       | Technology                          |
|-----------------|-------------------------------------|
| Backend API     | FastAPI + Uvicorn                   |
| Frontend        | Streamlit                           |
| Orchestration   | LangChain                           |
| Vector Store    | ChromaDB                            |
| LLM             | OpenAI GPT-3.5-turbo               |
| PDF Processing  | PyPDF                               |
| Configuration   | python-dotenv                       |

## Project Structure

```
financial-doc-chatbot/
├── backend/
│   ├── __init__.py
│   ├── server.py           # FastAPI app with /upload and /query
│   └── document_qa.py      # RAG pipeline (ingest, chunk, query)
├── frontend/
│   └── chat_ui.py          # Streamlit chat interface
├── data/                   # Uploaded PDFs (gitignored)
├── tests/
│   ├── test_document_qa.py
│   └── test_server.py
├── requirements.txt
├── pyproject.toml
├── .env.example
└── README.md
```

## License

MIT — see [LICENSE](LICENSE) for details.

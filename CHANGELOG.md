# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-04-13

### Added
- FastAPI backend with PDF upload and query endpoints.
- RAG pipeline: PDF ingestion, text chunking (1000/200), ChromaDB vector storage, conversational retrieval with memory.
- Streamlit chat UI with document upload sidebar and message history.
- Source citation display in query responses.
- Multi-turn conversation support via LangChain ConversationBufferMemory.
- Test suite with mocked external services.
- CI/CD pipeline with GitHub Actions.
- Project documentation (README, CONTRIBUTING, LICENSE).

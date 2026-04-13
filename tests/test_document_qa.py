"""Tests for the RAG pipeline (document_qa module).

All external services (OpenAI, ChromaDB, PDF loading) are mocked.
"""

import types
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_env(monkeypatch):
    """Ensure OPENAI_API_KEY is set so dotenv loading never fails."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-not-real")


@pytest.fixture()
def pipeline(mock_env):
    """Create a RAGPipeline with all heavy dependencies mocked out."""
    with (
        patch("backend.document_qa.OpenAIEmbeddings") as mock_embed,
        patch("backend.document_qa.Chroma") as mock_chroma,
        patch("backend.document_qa.ChatOpenAI") as mock_llm,
        patch("backend.document_qa.ConversationalRetrievalChain") as mock_chain_cls,
    ):
        mock_db_instance = MagicMock()
        mock_chroma.return_value = mock_db_instance
        mock_db_instance.as_retriever.return_value = MagicMock()

        mock_chain_instance = MagicMock()
        mock_chain_cls.from_llm.return_value = mock_chain_instance

        from backend.document_qa import RAGPipeline

        pipe = RAGPipeline(persist_directory="/tmp/test-vectordb")

        # Expose mocks for assertions
        pipe._mock_db = mock_db_instance
        pipe._mock_chain = mock_chain_instance
        yield pipe


# ---------------------------------------------------------------------------
# Tests: ingest_pdf
# ---------------------------------------------------------------------------

class TestIngestPdf:
    """Tests for RAGPipeline.ingest_pdf."""

    @patch("backend.document_qa.RecursiveCharacterTextSplitter")
    @patch("backend.document_qa.PyPDFLoader")
    def test_ingest_returns_chunk_count(self, mock_loader_cls, mock_splitter_cls, pipeline):
        """ingest_pdf should return the number of chunks produced."""
        fake_pages = [MagicMock(), MagicMock()]
        mock_loader_cls.return_value.load.return_value = fake_pages

        fake_chunks = [MagicMock() for _ in range(5)]
        mock_splitter_cls.return_value.split_documents.return_value = fake_chunks

        count = pipeline.ingest_pdf("/tmp/sample.pdf")

        assert count == 5
        mock_loader_cls.assert_called_once_with("/tmp/sample.pdf")
        mock_splitter_cls.return_value.split_documents.assert_called_once_with(fake_pages)
        pipeline._mock_db.add_documents.assert_called_once_with(fake_chunks)
        pipeline._mock_db.persist.assert_called_once()

    @patch("backend.document_qa.RecursiveCharacterTextSplitter")
    @patch("backend.document_qa.PyPDFLoader")
    def test_ingest_empty_pdf(self, mock_loader_cls, mock_splitter_cls, pipeline):
        """An empty PDF should produce zero chunks without errors."""
        mock_loader_cls.return_value.load.return_value = []
        mock_splitter_cls.return_value.split_documents.return_value = []

        count = pipeline.ingest_pdf("/tmp/empty.pdf")

        assert count == 0


# ---------------------------------------------------------------------------
# Tests: query
# ---------------------------------------------------------------------------

class TestQuery:
    """Tests for RAGPipeline.query."""

    def test_query_returns_answer_and_sources(self, pipeline):
        """query() should return answer text and deduplicated source list."""
        source_doc_1 = MagicMock()
        source_doc_1.metadata = {"source": "report_2024.pdf"}
        source_doc_2 = MagicMock()
        source_doc_2.metadata = {"source": "report_2024.pdf"}  # duplicate
        source_doc_3 = MagicMock()
        source_doc_3.metadata = {"source": "balance_q3.pdf"}

        pipeline._mock_chain.invoke.return_value = {
            "answer": "Revenue grew 12%.",
            "source_documents": [source_doc_1, source_doc_2, source_doc_3],
        }

        result = pipeline.query("What was the revenue growth?")

        assert result["answer"] == "Revenue grew 12%."
        assert result["sources"] == ["report_2024.pdf", "balance_q3.pdf"]
        pipeline._mock_chain.invoke.assert_called_once_with(
            {"question": "What was the revenue growth?"}
        )

    def test_query_no_answer(self, pipeline):
        """When chain returns no answer key, default text is used."""
        pipeline._mock_chain.invoke.return_value = {
            "source_documents": [],
        }

        result = pipeline.query("Unknown question?")

        assert result["answer"] == "No answer found."
        assert result["sources"] == []

    def test_query_no_source_documents(self, pipeline):
        """When no source_documents key exists, sources should be empty."""
        pipeline._mock_chain.invoke.return_value = {
            "answer": "Some answer.",
        }

        result = pipeline.query("Anything?")

        assert result["sources"] == []

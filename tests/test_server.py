"""Tests for the FastAPI server endpoints.

The RAG pipeline is fully mocked so no OpenAI/ChromaDB calls are made.
"""

import io
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def client():
    """Create a TestClient with the pipeline mocked."""
    with patch("backend.server.RAGPipeline") as mock_pipeline_cls:
        mock_pipeline = MagicMock()
        mock_pipeline_cls.return_value = mock_pipeline

        # Re-import to trigger module-level pipeline creation with our mock
        import importlib
        import backend.server
        importlib.reload(backend.server)

        from backend.server import app

        # Make the module-level pipeline point to our mock
        backend.server.pipeline = mock_pipeline

        yield TestClient(app), mock_pipeline


# ---------------------------------------------------------------------------
# Tests: POST /upload/
# ---------------------------------------------------------------------------

class TestUploadEndpoint:
    """Tests for the /upload/ endpoint."""

    def test_upload_valid_pdf(self, client, tmp_path):
        """Uploading a .pdf file should succeed and call ingest_pdf."""
        test_client, mock_pipeline = client
        mock_pipeline.ingest_pdf.return_value = 10

        pdf_bytes = b"%PDF-1.4 fake content"
        response = test_client.post(
            "/upload/",
            files={"file": ("annual_report.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
        )

        assert response.status_code == 200
        assert response.json()["status"] == "PDF ingested successfully"
        mock_pipeline.ingest_pdf.assert_called_once()

    def test_upload_non_pdf_rejected(self, client):
        """Non-PDF files should be rejected with 400."""
        test_client, _ = client

        response = test_client.post(
            "/upload/",
            files={"file": ("notes.txt", io.BytesIO(b"hello"), "text/plain")},
        )

        assert response.status_code == 400
        assert "PDF" in response.json()["detail"]

    def test_upload_ingestion_failure(self, client):
        """If ingestion raises, the endpoint should return 500."""
        test_client, mock_pipeline = client
        mock_pipeline.ingest_pdf.side_effect = RuntimeError("ChromaDB down")

        response = test_client.post(
            "/upload/",
            files={"file": ("report.pdf", io.BytesIO(b"%PDF-1.4 data"), "application/pdf")},
        )

        assert response.status_code == 500
        assert "Ingestion failed" in response.json()["detail"]


# ---------------------------------------------------------------------------
# Tests: GET /query/
# ---------------------------------------------------------------------------

class TestQueryEndpoint:
    """Tests for the /query/ endpoint."""

    def test_query_returns_answer(self, client):
        """A valid query should return answer and sources."""
        test_client, mock_pipeline = client
        mock_pipeline.query.return_value = {
            "answer": "Net income was $5M.",
            "sources": ["income_stmt.pdf"],
        }

        response = test_client.get("/query/", params={"q": "What was net income?"})

        assert response.status_code == 200
        body = response.json()
        assert body["answer"] == "Net income was $5M."
        assert body["sources"] == ["income_stmt.pdf"]

    def test_query_empty_string_rejected(self, client):
        """An empty query string should be rejected with 400."""
        test_client, _ = client

        response = test_client.get("/query/", params={"q": "   "})

        assert response.status_code == 400

    def test_query_pipeline_failure(self, client):
        """If the pipeline raises, the endpoint should return 500."""
        test_client, mock_pipeline = client
        mock_pipeline.query.side_effect = RuntimeError("LLM timeout")

        response = test_client.get("/query/", params={"q": "question"})

        assert response.status_code == 500
        assert "Query failed" in response.json()["detail"]

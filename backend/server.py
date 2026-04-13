"""FastAPI backend for the financial document chatbot.

Provides endpoints for PDF upload and conversational querying
against ingested documents.
"""

import os
import shutil
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile

from backend.document_qa import RAGPipeline

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

app = FastAPI(
    title="Financial Doc Chatbot API",
    description="Upload financial PDFs and ask questions with source citations.",
    version="1.0.0",
)

pipeline = RAGPipeline()


@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload a PDF document for ingestion into the RAG pipeline."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    os.makedirs(DATA_DIR, exist_ok=True)
    dest = os.path.join(DATA_DIR, file.filename)

    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        pipeline.ingest_pdf(dest)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {exc}")

    return {"status": "PDF ingested successfully"}


@app.get("/query/")
async def query_documents(q: str):
    """Query the ingested documents with a natural-language question."""
    if not q.strip():
        raise HTTPException(status_code=400, detail="Query parameter 'q' must not be empty.")

    try:
        result = pipeline.query(q)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Query failed: {exc}")

    return {"answer": result["answer"], "sources": result["sources"]}

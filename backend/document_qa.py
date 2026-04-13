"""RAG pipeline for financial document question-answering.

Handles PDF ingestion, text chunking, vector storage via ChromaDB,
and conversational retrieval with source citations.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
PERSIST_DIR = os.path.join(os.path.dirname(__file__), "..", "vectordb")
LLM_MODEL = "gpt-3.5-turbo"
LLM_TEMPERATURE = 0


class RAGPipeline:
    """Retrieval-Augmented Generation pipeline for document Q&A."""

    def __init__(self, persist_directory: str | None = None) -> None:
        load_dotenv()

        self._persist_dir = persist_directory or PERSIST_DIR

        self._embeddings = OpenAIEmbeddings()
        self._vectordb = Chroma(
            persist_directory=self._persist_dir,
            embedding_function=self._embeddings,
        )

        self._llm = ChatOpenAI(model=LLM_MODEL, temperature=LLM_TEMPERATURE)

        self._memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer",
        )

        self._chain = ConversationalRetrievalChain.from_llm(
            llm=self._llm,
            retriever=self._vectordb.as_retriever(),
            memory=self._memory,
            return_source_documents=True,
            output_key="answer",
        )

    def ingest_pdf(self, pdf_path: str) -> int:
        """Load a PDF, chunk it, and store embeddings in the vector database.

        Args:
            pdf_path: Filesystem path to the PDF file.

        Returns:
            Number of chunks created from the document.
        """
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )
        chunks = splitter.split_documents(pages)

        self._vectordb.add_documents(chunks)
        self._vectordb.persist()

        return len(chunks)

    def query(self, question: str) -> dict:
        """Ask a question against the ingested documents.

        Args:
            question: Natural-language question string.

        Returns:
            Dict with "answer" (str) and "sources" (list[str]).
        """
        result = self._chain.invoke({"question": question})

        answer = result.get("answer", "No answer found.")

        sources: list[str] = []
        for doc in result.get("source_documents", []):
            source = doc.metadata.get("source", "")
            if source and source not in sources:
                sources.append(source)

        return {"answer": answer, "sources": sources}

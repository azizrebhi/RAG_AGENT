# ingest.py (UPDATED ✅)
import os, uuid
from typing import List
from dotenv import load_dotenv
load_dotenv()

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance

from sentence_transformers import SentenceTransformer

from models import EMBED_MODEL, QDRANT_URL, QDRANT_COLLECTION

# Init embedding + vector DB client
qc = QdrantClient(url=QDRANT_URL)
embed_model = SentenceTransformer(EMBED_MODEL)
DIM = embed_model.get_sentence_embedding_dimension()

def ensure_collection():
    """Create collection if it does not exist."""
    collections = [c.name for c in qc.get_collections().collections]
    if QDRANT_COLLECTION not in collections:
        qc.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(
                size=DIM,
                distance=Distance.COSINE,
            ),
        )
        print(f"✅ Qdrant collection created: {QDRANT_COLLECTION}")
    else:
        print(f"ℹ️ Qdrant collection exists: {QDRANT_COLLECTION}")

def ingest_pdfs(filepaths: List[str], chunk_size: int = 800, chunk_overlap: int = 150) -> int:
    """
    Loads PDFs, splits into chunks, embeds, and upserts into Qdrant.
    Returns number of chunks inserted.
    """
    ensure_collection()

    all_docs = []
    for path in filepaths:
        loader = PyPDFLoader(path)
        docs = loader.load()
        for d in docs:
            d.metadata = d.metadata or {}
            d.metadata["source"] = os.path.basename(path)
        all_docs.extend(docs)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunks = splitter.split_documents(all_docs)
    if not chunks:
        return 0

    points = []
    for i, chunk in enumerate(chunks):
        text = chunk.page_content.strip()
        cid = str(uuid.uuid4())
        vector = embed_model.encode(text).tolist()
        payload = {
            "source": chunk.metadata.get("source", "unknown"),
            "chunk_id": i,  # ordered chunks for visibility
            "text": text[:1500],  # preview only
        }
        points.append({"id": cid, "vector": vector, "payload": payload})

    # Batch insert
    BATCH_SIZE = 64
    for i in range(0, len(points), BATCH_SIZE):
        qc.upsert(
            collection_name=QDRANT_COLLECTION,
            points=points[i:i + BATCH_SIZE]
        )

    print(f"✅ Ingested {len(points)} chunks → collection '{QDRANT_COLLECTION}'")
    return len(points)

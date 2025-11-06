# rag_core.py ✅ Final Updated Version
import os
from typing import List, Dict
from dotenv import load_dotenv
load_dotenv()

import subprocess
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance
from sentence_transformers import SentenceTransformer

from models import EMBED_MODEL, QDRANT_URL, QDRANT_COLLECTION, MODEL_NAME, TOP_K, SCORE_THRESHOLD

# Initialize embedding model
embed_model = SentenceTransformer(EMBED_MODEL)
EMBED_DIM = embed_model.get_sentence_embedding_dimension()

# Qdrant client
qc = QdrantClient(url=QDRANT_URL)

def init_qdrant():
    """Ensure Qdrant collection exists before searching or adding."""
    collections = [c.name for c in qc.get_collections().collections]
    if QDRANT_COLLECTION not in collections:
        qc.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(
                size=EMBED_DIM,
                distance=Distance.COSINE,
            ),
        )
        print(f"✅ Created Qdrant collection: {QDRANT_COLLECTION}")
    else:
        pass  # silent success

def retrieve(query: str, top_k: int = TOP_K, score_threshold: float = SCORE_THRESHOLD) -> List[Dict]:
    """Retrieve relevant document chunks based on semantic similarity."""
    init_qdrant()  # ✅ Ensure collection exists

    qvec = embed_model.encode(query).tolist()

    try:
        result = qc.search(
            collection_name=QDRANT_COLLECTION,
            query_vector=qvec,
            with_payload=True,
            limit=top_k
        )
    except Exception:
        return []  # ✅ If search fails (e.g. empty), return no docs

    docs = []
    for r in result:
        score = float(r.score or 0.0)
        if score < score_threshold:
            continue
        docs.append({
            "id": r.id,
            "score": score,
            "source": r.payload.get("source", "unknown"),
            "chunk_id": r.payload.get("chunk_id"),
            "text": r.payload.get("text", "")
        })
    return docs

def build_rag_prompt(query: str, docs: List[Dict]) -> str:
    """Construct structured context with citations."""
    if not docs:
        return (
            "No relevant context found. "
            "If you are referring to uploaded documents, please upload or ingest them first.\n\n"
            f"QUESTION: {query}"
        )

    context = "\n\n".join(
        f"[{d['source']} | chunk:{d['chunk_id']} | score:{d['score']:.2f}]\n{d['text']}"
        for d in docs
    )

    return (
        "Answer ONLY using the provided CONTEXT. "
        "If not found, say: 'I don't know based on the uploaded documents.'\n\n"
        f"CONTEXT:\n{context}\n\nQUESTION:\n{query}\n\n"
        "Provide a brief answer with inline citations [source: filename]."
    )

def call_ollama(prompt: str) -> str:
    try:
        cmd = ["ollama", "run", MODEL_NAME]
        proc = subprocess.run(
            cmd,
            input=prompt.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=200
        )
        if proc.returncode == 0:
            return proc.stdout.decode("utf-8", errors="ignore").strip()
        return "[LLM ERROR] " + proc.stderr.decode("utf-8", errors="ignore").strip()
    except Exception as e:
        return f"[LLM ERROR] {str(e)}"


def answer_query(query: str, conv_id: str = "default") -> Dict:
    """Main entrypoint: retrieve, build prompt, generate answer."""
    init_qdrant()

    docs = retrieve(query)

    # Graceful fallback if no documents indexed yet
    if not docs:
        return {
            "question": query,
            "answer": "I don't know based on the uploaded documents. Please ingest PDFs first.",
            "documents": []
        }

    prompt = build_rag_prompt(query, docs)
    answer = call_ollama(prompt)
    return {"question": query, "answer": answer, "documents": docs}

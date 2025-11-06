# 📚 Agentic RAG Local — Privacy-First AI Knowledge Assistant

A fully local Retrieval-Augmented Generation system that can read and answer questions using **your PDFs only** — no cloud, no data leak, 100% offline.

---

## ✨ Features

- ✅ Upload and index PDFs
- ✅ Local LLM inference with Ollama (Phi-3-tiny)
- ✅ Semantic vector search via Qdrant
- ✅ Accurate answers with document citations
- ✅ Multiple conversation memory
- ✅ Modern UI with Streamlit

---

## 🧩 Tech Stack

| Component | Role |
|----------|------|
| Python | App logic |
| Streamlit | User interface |
| SentenceTransformers | Embeddings |
| Qdrant (Docker) | Vector storage & search |
| Ollama + Phi-3-tiny | Local LLM |

---

## ✅ Requirements

| Requirement | Minimum |
|------------|--------|
| Python | 3.10+ |
| RAM | 8 GB |
| Disk | 5 GB free |
| Docker | Installed & running |
| Ollama | Installed |

---

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/azizrebhi/RAG_AGENT.git
cd RAG_AGENT

# Create & activate venv
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
copy .env.example .env
```

### 🐳 Start Qdrant

```bash
docker run -d --name qdrant \
  -p 6333:6333 -p 6334:6334 \
  qdrant/qdrant:latest
```
Dashboard: http://localhost:6333/dashboard

### 🤖 Install Local Model

```bash
ollama pull phi3:tiny
```

### ▶️ Run the App

```bash
streamlit run app.py
```

## 📝 How to Use

1. Upload PDFs in the sidebar
2. Click "Ingest PDFs"
3. Ask questions in the chat box
4. View answers + cited document chunks

### Example Questions

```sql
What is Value-at-Risk?
Explain Monte-Carlo simulation in risk management.
```

## 🧱 Architecture

```
Streamlit UI → RAG Core → Qdrant (search)
                       → Ollama (LLM generation)
✅ Everything stays local
```

## 📁 Project Structure

```
rag-agentic-local/
├─ app.py
├─ rag_core.py
├─ ingest.py
├─ memory.py
├─ models.py
|
├─ uploads/           # temporary PDF storage (ignored in git)
├─ conversations/     # conversation memory (ignored in git)
|
├─ requirements.txt
├─ README.md
└─ .env.example
```

## ❗ Troubleshooting

| Issue | Fix |
|-------|-----|
| LLM fails to load | Use smaller model: phi3:tiny |
| No results | Ensure PDFs ingested successfully |
| Qdrant 404 | Start Docker Qdrant container |
| Unicode issues | UTF-8 fixed in subprocess handling |

## 🔮 Roadmap

- [ ] Better citation ranking
- [ ] PDF viewer with highlighted answers
- [ ] Full Docker Compose deployment
- [ ] Conversation summarization
- [ ] RAG with web deep-research mode

## 🏆 Credits

- [Qdrant](https://qdrant.tech/) — Vector Database
- [Ollama](https://ollama.ai/) — Local LLM runtime
- [Streamlit](https://streamlit.io/) — UI Framework
- [SentenceTransformers](https://www.sbert.net/) — Embedding model

Built by Maison Info 🧠⚡  
Guided by Agentic AI Engineering 🤝
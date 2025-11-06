# app.py
import streamlit as st
import os, uuid
from dotenv import load_dotenv
load_dotenv()

from ingest import ingest_pdfs
from rag_core import answer_query, retrieve
from memory import load_conversation, save_message, list_conversations
from models import TOP_K

st.set_page_config(page_title="Agentic RAG Local", layout="wide")
st.title("📚 Agentic RAG — Local Demo (Phi-3-mini)")

# Sidebar: conversation management & ingestion
with st.sidebar:
    st.header("Conversations")
    convs = list_conversations()
    new_name = st.text_input("New conversation name")
    if st.button("Create conversation"):
        if new_name.strip():
            cid = new_name.strip().replace(" ", "_")
            path = f"conversations/{cid}.json"
            if not os.path.exists(path):
                with open(path, "w", encoding="utf-8") as f:
                    f.write('{"id":"%s","messages":[]}' % cid)
            st.success(f"Created conv: {cid}")
            convs = list_conversations()

    selected_conv = st.selectbox("Select conversation", options=(convs or ["default"]))
    st.markdown("---")
    st.header("Upload PDFs")
    uploads = st.file_uploader("Upload PDFs", accept_multiple_files=True, type=["pdf"])
    if st.button("Ingest PDFs"):
        if not uploads:
            st.warning("Please upload at least one PDF")
        else:
            paths = []
            for f in uploads:
                tmp = f"uploads/{uuid.uuid4().hex[:8]}_{f.name}"
                os.makedirs("uploads", exist_ok=True)
                with open(tmp, "wb") as out:
                    out.write(f.read())
                paths.append(tmp)
            with st.spinner("Ingesting..."):
                n = ingest_pdfs(paths)
            st.success(f"Ingested {n} chunks")

    st.markdown("---")
    st.markdown("Qdrant status: connect to your local Docker Qdrant at port 6333")

# Main area: conversation
st.header(f"Conversation: {selected_conv}")
conv = load_conversation(selected_conv)

# show history
for msg in conv.get("messages", []):
    st.markdown(f"**User:** {msg['user']}")
    st.markdown(f"**Assistant:** {msg['assistant']}")
    if msg.get("docs"):
        st.markdown("Sources used:")
        for d in msg["docs"]:
            st.markdown(f"- **{d['source']}** — chunk `{d['chunk_id']}` — score `{d['score']:.3f}`")
    st.markdown("---")

# query
q = st.text_input("Ask a question (the assistant will search uploaded PDFs):")
if st.button("Ask"):
    if not q.strip():
        st.warning("Enter a question first")
    else:
        with st.spinner("Retrieving and answering..."):
            res = answer_query(q, conv_id=selected_conv)
        # show answer
        st.markdown("### Answer")
        st.write(res["answer"])
        # show retrieved docs
        docs = res.get("documents", [])
        if docs:
            st.markdown("### Retrieved evidence")
            for d in docs:
                with st.expander(f"{d['source']} — chunk {d['chunk_id']} — score {d['score']:.3f}"):
                    st.write(d["text"])
        else:
            st.info("No strong matches found in uploaded docs (the assistant may not be grounded).")

        # save to conversation
        save_message(selected_conv, q, res["answer"], docs)
        st.rerun()

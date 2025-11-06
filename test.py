from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("tt.pdf")
docs = loader.load()

print("Pages loaded:", len(docs))
print("First 500 chars:\n", docs[0].page_content[:500])
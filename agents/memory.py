"""
Memory Management (RAG) using ChromaDB & Ollama Embeddings.
Allows the agents to learn from past architectures.
"""

import os
from langchain_chroma import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# Use nomic-embed-text for fast, local embeddings
embeddings = OllamaEmbeddings(model="nomic-embed-text")
DB_DIR = "./chroma_db"

def get_vector_store():
    """Initializes or loads the ChromaDB vector store."""
    return Chroma(
        collection_name="architecture_memory",
        embedding_function=embeddings,
        persist_directory=DB_DIR
    )

def train_memory(path: str):
    """
    Reads all code/text in a directory, chunks it,
    and stores it in the local Vector Database.
    """
    if not os.path.exists(path):
        print("⚠️ Path does not exist.")
        return

    print(f"🧠 Reading codebase for training from: {path}")
    docs = []

    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            docs.append(Document(page_content=content, metadata={"source": path}))
        except Exception as e:
            print(f"Error reading file {path}: {e}")
    else:
        allowed_exts = {".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".cpp", ".c", ".h", ".go", ".rs", ".cs", ".rb", ".php", ".md", ".txt"}
        for root, _, files in os.walk(path):
            if any(part.startswith('.') for part in root.split(os.sep)) or "node_modules" in root or "venv" in root or "__pycache__" in root:
                continue
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in allowed_exts:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            docs.append(Document(page_content=f.read(), metadata={"source": file_path}))
                    except Exception:
                        pass
    
    if not docs:
        print("⚠️ No valid code or text files found to train on.")
        return

    print(f"✂️ Chunking {len(docs)} files into smaller memory fragments...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)

    print(f"💾 Saving {len(splits)} memory fragments to VectorDB (Chroma)...")
    vector_store = get_vector_store()
    vector_store.add_documents(splits)
    print("✅ Training complete. Agents will now remember this architecture.")

def retrieve_memory(query: str, k: int = 3) -> str:
    """
    Searches the VectorDB for past architectural decisions
    similar to the query.
    """
    if not os.path.exists(DB_DIR):
        return "No past architectural memory found. ChromaDB is empty."
        
    vector_store = get_vector_store()
    results = vector_store.similarity_search(query, k=k)
    
    if not results:
        return "No relevant past memory found."
        
    memory_text = "\n\n".join([f"[Source: {doc.metadata.get('source', 'Unknown')}]\n{doc.page_content}" for doc in results])
    return memory_text

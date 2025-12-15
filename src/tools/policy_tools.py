from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings # <--- Back to Google
from langchain_core.tools import tool
from src.config import POLICY_DOC_PATH, DATA_DIR, GOOGLE_API_KEY
import os

# Define where to save the "Brain" (Embeddings)
VECTOR_STORE_PATH = os.path.join(DATA_DIR, "vector_store_cache")

_vector_store = None

def get_vector_store():
    global _vector_store
    if _vector_store is not None:
        return _vector_store

    # 1. Initialize Google Embeddings
    # This uses your quota, but only during creation.
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004", 
        google_api_key=GOOGLE_API_KEY
    )

    # 2. Check if we already have a saved "Brain" on disk
    if os.path.exists(VECTOR_STORE_PATH):
        print("⚡ Loading policy embeddings from disk cache (No API Cost)...")
        try:
            # Load from disk (Super Fast)
            _vector_store = FAISS.load_local(
                VECTOR_STORE_PATH, 
                embeddings, 
                allow_dangerous_deserialization=True
            )
            return _vector_store
        except Exception as e:
            print(f"⚠️ Cache corrupted, rebuilding... ({e})")

    # 3. If NOT found on disk, create it from scratch (Costs API Quota)
    print("🔄 Generating NEW embeddings via Google API (One-time process)...")
    if not os.path.exists(POLICY_DOC_PATH):
        print(f"❌ Error: Policy PDF not found at {POLICY_DOC_PATH}")
        return None

    loader = PyPDFLoader(POLICY_DOC_PATH)
    pages = loader.load_and_split()
    
    # Create Vector Store
    _vector_store = FAISS.from_documents(pages, embeddings)
    
    # 4. SAVE it to disk for next time
    _vector_store.save_local(VECTOR_STORE_PATH)
    print(f"✅ Embeddings saved to {VECTOR_STORE_PATH}")
        
    return _vector_store

@tool
def search_return_policy(query: str):
    """
    Searches the official ABFRL Return & Exchange Policy document.
    """
    try:
        vector_store = get_vector_store()
        if not vector_store:
            return "Policy document is not available."
            
        docs = vector_store.similarity_search(query, k=2)
        context = "\n".join([doc.page_content for doc in docs])
        return f"Policy Context:\n{context}"
    except Exception as e:
        return f"Error searching policy: {str(e)}"
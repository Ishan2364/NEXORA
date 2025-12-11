from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.tools import tool
from src.config import POLICY_DOC_PATH, GOOGLE_API_KEY
import os

# Initialize Vector Store (Lazy loading to avoid startup cost if not needed)
_vector_store = None

def get_vector_store():
    global _vector_store
    if _vector_store is None:
        if not os.path.exists(POLICY_DOC_PATH):
            return None
        loader = PyPDFLoader(POLICY_DOC_PATH)
        pages = loader.load_and_split()
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)
        _vector_store = FAISS.from_documents(pages, embeddings)
    return _vector_store

@tool
def search_return_policy(query: str):
    """
    Searches the official ABFRL Return & Exchange Policy document.
    Use this when customers ask about return windows, non-returnable items, or refund timelines.
    """
    try:
        vector_store = get_vector_store()
        if not vector_store:
            return "Policy document is not available."
            
        # Retrieve top 2 relevant chunks
        docs = vector_store.similarity_search(query, k=2)
        context = "\n".join([doc.page_content for doc in docs])
        return f"Policy Context:\n{context}"
    except Exception as e:
        return f"Error searching policy: {str(e)}"
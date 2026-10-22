import chromadb
from langchain_chroma import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from app.config import CHROMA_HOST, CHROMA_PORT, OLLAMA_BASE_URL, EMBEDDING_MODEL_NAME

def get_embedding_function():
    """Initialise le modèle d'embedding local via Ollama."""
    return OllamaEmbeddings(
        base_url=OLLAMA_BASE_URL,
        model=EMBEDDING_MODEL_NAME
    )

def get_vector_store(collection_name: str = "recipes") -> Chroma:
    """Connecte l'API au serveur ChromaDB."""
    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    
    vector_store = Chroma(
        client=client,
        collection_name=collection_name,
        embedding_function=get_embedding_function()
    )
    return vector_store
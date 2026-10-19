from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import logging

from app.config import CHROMA_HOST, CHROMA_PORT, OLLAMA_BASE_URL
from app.core.db import get_vector_store

from app.api.routes_ingestion import router as ingestion_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API Assistant Culinaire",
    description="Moteur de génération sous contraintes et système RAG pour la gestion de recettes.",
    version="1.0.0"
)

# Configuration CORS pour autoriser l'UI Streamlit (Livrable 4)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En prod, restreindre à l'URL Streamlit
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Vérification de la connectivité au démarrage de l'API."""
    logger.info("Démarrage de l'application...")
    
    # 1. Test de connexion à Ollama
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            logger.info("✅ Connexion réussie au service Ollama")
        else:
            logger.warning("⚠️ Le service Ollama a répondu avec un statut non valide.")
    except Exception as e:
        logger.error(f"❌ Impossible de joindre le service Ollama ({OLLAMA_BASE_URL}): {e}")

    # 2. Test de connexion à ChromaDB
    try:
        store = get_vector_store()
        logger.info("✅ Connexion réussie à ChromaDB")
    except Exception as e:
        logger.error(f"❌ Impossible de se connecter à ChromaDB ({CHROMA_HOST}:{CHROMA_PORT}): {e}")

@app.get("/", tags=["Healthcheck"])
def read_root():
    return {
        "status": "online",
        "message": "Bienvenue sur l'API du Moteur de Génération et RAG Culinaire"
    }


app.include_router(ingestion_router, prefix="/api/v1", tags=["Ingestion"])



# Inclusions ultérieures des routes
# from app.api.routes_generation import router as generation_router
# from app.api.routes_rag import router as rag_router

# app.include_router(generation_router, prefix="/api/v1", tags=["Generation"])
# app.include_router(rag_router, prefix="/api/v1", tags=["RAG"])
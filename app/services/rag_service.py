from langchain_community.llms import Ollama
from app.config import OLLAMA_BASE_URL
from app.core.db import get_vector_store
from app.core.carbon import track_emissions
import logging

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        self.llm = Ollama(
            base_url=OLLAMA_BASE_URL,
            model="qwen2:1.5b",
            temperature=0.3
        )
        self.vector_store = get_vector_store("recipes")

    def chat(self, message: str, history: list[dict] = None) -> dict:
        history = history or []
        
        # 1. Recherche dans ChromaDB (Retrieval)
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 2})
        relevant_docs = retriever.invoke(message)
        
        # Extraction du texte et des sources
        context_texts = []
        sources = []
        
        for doc in relevant_docs:
            context_texts.append(doc.page_content)
            title = doc.metadata.get("title", "Recette inconnue")
            url = doc.metadata.get("url", "")
            sources.append({"title": title, "url": url})

        context_str = "\n\n---\n\n".join(context_texts)

        # 2. Reconstitution de l'historique pour le prompt
        history_str = ""
        for msg in history:
            role = "Utilisateur" if msg.get("role") == "user" else "Assistant"
            history_str += f"{role}: {msg.get('content')}\n"

        # 3. Prompt RAG
        prompt = f"""Tu es un assistant culinaire expert et bienveillant.
Réponds à la question de l'utilisateur en appuyant tes conseils sur les recettes de contexte fournies ci-dessous.
Si les recettes fournies ne permettent pas de répondre directement, utilise tes connaissances en cuisine tout en restant prudent.

RECETTES DE CONTEXTE (BDD) :
{context_str}

HISTORIQUE DE LA CONVERSATION :
{history_str}

QUESTION DE L'UTILISATEUR :
{message}

RÉPONSE :"""

        # 4. Exécution avec mesure CodeCarbon
        tracker = track_emissions("rag_chat")
        tracker.start()
        
        try:
            response_text = self.llm.invoke(prompt)
        finally:
            emissions = tracker.stop()
            logger.info(f"🌱 Émissions RAG : {emissions} kgCO2eq")

        return {
            "response": response_text.strip(),
            "sources": sources,
            "emissions_kgco2eq": emissions
        }
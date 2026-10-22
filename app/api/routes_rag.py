from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services.rag_service import RAGService

router = APIRouter()
rag_service = RAGService()

class ChatMessageDTO(BaseModel):
    role: str  # "user" ou "assistant"
    content: str

class ChatRequestDTO(BaseModel):
    message: str
    history: Optional[List[ChatMessageDTO]] = []

@router.post("/chat", summary="Agent RAG conversationnel avec historique et sources")
def chat_endpoint(req: ChatRequestDTO):
    """
    Pose une question au RAG. L'API interroge ChromaDB, conserve l'historique et cite les sources.
    """
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Le message ne peut pas être vide.")

    try:
        history_dict = [msg.model_dump() for msg in req.history]
        result = rag_service.chat(
            message=req.message,
            history=history_dict
        )
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur RAG : {str(e)}")
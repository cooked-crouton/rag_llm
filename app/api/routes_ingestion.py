from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services.ingestion_service import IngestionService

router = APIRouter()
ingestion_service = IngestionService()

class IngredientDTO(BaseModel):
    name: str
    quantity: Optional[str] = None
    unit: Optional[str] = None

class RecipeVectorizedDTO(BaseModel):
    url: str
    title: str
    ingredients: List[IngredientDTO] = []
    steps: List[str] = []
    cook_time: Optional[str] = None
    embedding: List[float]  # Le vecteur pré-calculé par le scraper

@router.post("/ingest", summary="Ingérer les recettes déjà vectorisées")
def ingest_recipes(recipes: List[RecipeVectorizedDTO]):
    """
    Endpoint appelé par le scraper pour envoyer les recettes JSON vectorisées.
    """
    try:
        count = ingestion_service.add_precomputed_recipes([r.model_dump() for r in recipes])
        return {
            "status": "success",
            "message": f"{count} recettes insérées avec succès dans ChromaDB."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d'ingestion : {str(e)}")
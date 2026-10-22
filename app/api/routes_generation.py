from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services.generation_service import GenerationService

router = APIRouter()
gen_service = GenerationService()

class GenerationRequest(BaseModel):
    ingredients: List[str]
    dietary_constraints: Optional[List[str]] = []

@router.post("/generate", summary="Générer une recette sous contraintes (Frigo Vide)")
def generate_recipe_endpoint(req: GenerationRequest):
    """
    Génère une recette à partir d'une liste d'ingrédients restreinte et enregistre l'empreinte carbone.
    """
    if not req.ingredients:
        raise HTTPException(status_code=400, detail="La liste d'ingrédients ne peut pas être vide.")

    try:
        recipe = gen_service.generate_recipe(
            ingredients=req.ingredients,
            dietary_constraints=req.dietary_constraints
        )
        return {
            "status": "success",
            "recipe": recipe
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération : {str(e)}")
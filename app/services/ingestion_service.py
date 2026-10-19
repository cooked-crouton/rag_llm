import hashlib
import chromadb
from typing import List, Dict, Any
from app.config import CHROMA_HOST, CHROMA_PORT

class IngestionService:
    def __init__(self, collection_name: str = "recipes"):
        self.client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        # On récupère ou crée la collection
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def _format_recipe_to_text(self, recipe: Dict[str, Any]) -> str:
        """Met en forme la recette en texte clair pour la recherche RAG."""
        ingredients_formatted = []
        for ing in recipe.get("ingredients", []):
            qty = f" {ing['quantity']}" if ing.get("quantity") else ""
            unit = f" {ing['unit']}" if ing.get("unit") else ""
            ingredients_formatted.append(f"{ing['name']}{qty}{unit}")

        steps_formatted = "\n".join([f"{i+1}. {step}" for i, step in enumerate(recipe.get("steps", []))])

        return (
            f"Titre : {recipe['title']}\n"
            f"Temps de cuisson : {recipe.get('cook_time') or 'Non précisé'}\n"
            f"Ingrédients : {', '.join(ingredients_formatted)}\n"
            f"Étapes :\n{steps_formatted}"
        )

    def add_precomputed_recipes(self, recipes: List[Dict[str, Any]]) -> int:
        ids = []
        embeddings = []
        documents = []
        metadatas = []

        for recipe in recipes:
            recipe_id = hashlib.md5(recipe["url"].encode()).hexdigest()
            doc_text = self._format_recipe_to_text(recipe)
            ing_names = [ing["name"] for ing in recipe.get("ingredients", [])]

            ids.append(recipe_id)
            embeddings.append(recipe["embedding"])
            documents.append(doc_text)
            metadatas.append({
                "url": recipe["url"],
                "title": recipe["title"],
                "cook_time": recipe.get("cook_time") or "",
                "ingredients_list": ", ".join(ing_names)
            })

        # Insertion directe des vecteurs
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        return len(ids)
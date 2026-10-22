from langchain_community.llms import Ollama
from app.config import OLLAMA_BASE_URL
from app.core.carbon import track_emissions
import json
import logging

logger = logging.getLogger(__name__)

class GenerationService:
    def __init__(self):
        # Modèle de génération texte (ex: llama3)
        self.llm = Ollama(
            base_url=OLLAMA_BASE_URL,
            model="qwen2:1.5b",
            temperature=0.2 # Faible température pour réduire les hallucinations
        )

    def generate_recipe(self, ingredients: list[str], dietary_constraints: list[str] = None) -> dict:
        constraints_str = ", ".join(dietary_constraints) if dietary_constraints else "Aucune"
        ingredients_str = ", ".join(ingredients)

        prompt = f"""Tu es un chef cuisinier expert.
Ta mission est de créer une recette cohérente, savoureuse et réaliste.

RÈGLES STRICTES :
1. Tu dois utiliser EXCLUSIVEMENT les ingrédients fournis dans la liste : [{ingredients_str}].
2. Tu peux uniquement ajouter des condiments de base : sel, poivre, eau, huile d'olive.
3. Ne rajoute AUCUN autre ingrédient principal (pas de banane avec de la moutarde, pas d'ingrédient hors liste).
4. Respecte les contraintes alimentaires suivantes : {constraints_str}.

FORMAT DE RÉPONSE OBLIGATOIRE :
Réponds UNIQUEMENT sous forme d'un objet JSON valide sans aucun texte avant ou après, avec la structure suivante :
{{
    "title": "Nom de la recette",
    "cook_time": "Temps estimé (ex: 20 min)",
    "used_ingredients": ["ingrédient 1", "ingrédient 2"],
    "steps": [
        "Étape 1...",
        "Étape 2..."
    ]
}}
"""

        # Mesure d'impact environnemental avec CodeCarbon
        tracker = track_emissions("recipe_generation")
        tracker.start()
        
        try:
            raw_response = self.llm.invoke(prompt)
        finally:
            emissions = tracker.stop()
            logger.info(f"🌱 Émissions carbone mesurées : {emissions} kgCO2eq")

        # Parsing de la réponse JSON
        try:
            # Extraction du bloc JSON si le modèle entoure de ```json ... ```
            cleaned_response = raw_response.strip()
            if "```json" in cleaned_response:
                cleaned_response = cleaned_response.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned_response:
                cleaned_response = cleaned_response.split("```")[1].strip()
                
            recipe_data = json.loads(cleaned_response)
            recipe_data["emissions_kgco2eq"] = emissions
            return recipe_data
        except json.JSONDecodeError:
            # Fallback si le LLM n'a pas renvoyé un JSON parfait
            return {
                "title": "Recette Générée",
                "raw_text": raw_response,
                "emissions_kgco2eq": emissions
            }
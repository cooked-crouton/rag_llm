# 🍳 Assistant Culinaire - Livrable 3 : Moteur de Génération & RAG

Ce projet constitue le **Livrable 3** de la plateforme intelligente de gestion culinaire. Il fournit un moteur de génération sous contraintes (mode « frigo vide ») ainsi qu'un agent conversationnel RAG (Retrieval-Augmented Generation) connecté à une base vectorielle locale ChromaDB et un modèle de langage (LLM) exécuté localement via Ollama.

---

## 🌟 Fonctionnalités Principales

- **Génération sous contraintes (« Frigo Vide »)** : Génération de recettes cohérentes et réalistes strictement limitées aux ingrédients fournis.
- **Agent Chatbot & RAG** : Réponses aux questions culinaires en interrogeant la base de recettes vectorisées, avec gestion de l'historique et sourçage systématique.
- **Mesure d'Impact Environnemental** : Intégration de `CodeCarbon` pour calculer l'empreinte carbone (kgCO2eq) générée par chaque inférence LLM.
- **Exécution 100% Locale & Confidentielle** : Respect strict du cahier des charges (aucune donnée transmise à un service cloud externe).

---

## 🏗️ Architecture Technique & Stack

- **Framework Web** : FastAPI (Python 3.11)
- **Base Vectorielle** : ChromaDB (mode serveur HTTP)
- **Modèle de Langage (LLM)** : Ollama (`qwen2:1.5b` ou `phi3`)
- **Orchestration LLM / RAG** : LangChain
- **Mesure Carbone** : CodeCarbon
- **Conteneurisation** : Docker & Docker Compose

---

## 🚀 Installation & Lancement

### Préréquis

- Docker et Docker Compose installés sur la machine hôte.

### 1. Démarrage des Conteneurs

À la racine du dossier `livrable_3/`, exécutez :

```bash
docker compose up -d --build
```

Cette commande démarre trois services :
1. `chromadb` (Port `8000`) : Serveur de base vectorielle.
2. `ollama` (Port `11434`) : Moteur d'exécution local du LLM.
3. `api` (Port `8080`) : L'API FastAPI du Livrable 3.

### 2. Téléchargement du Modèle LLM (À faire une seule fois)

Téléchargez le modèle ultra-léger recommandé pour le CPU dans le conteneur Ollama :

```bash
docker exec -it recipe_ollama ollama pull qwen2:1.5b
```

### 3. Accès à la Documentation Interactive

Une fois les conteneurs démarrés, ouvrez votre navigateur à l'adresse suivante :
👉 **Swagger UI** : [http://localhost:8080/docs](http://localhost:8080/docs)

---

## 📚 Documentation des Endpoints API

### 1. Ingestion de Recettes Vectorisées
- **Route** : `POST /api/v1/ingest`
- **Rôle** : Reçoit les recettes collectées et pré-vectorisées transmises par le **Livrable 1** pour alimenter le socle de connaissances ChromaDB.

#### Exemple de Requête (`POST`)
```json
[
  {
    "url": "https://www.marmiton.org/recettes/recette_pates-carbonara_12345.aspx",
    "title": "Pâtes Carbonara Traditionnelles",
    "ingredients": [
      {"name": "Pâtes", "quantity": "400", "unit": "g"},
      {"name": "Lardons", "quantity": "150", "unit": "g"},
      {"name": "Œufs", "quantity": "3", "unit": null},
      {"name": "Parmesan", "quantity": "50", "unit": "g"}
    ],
    "steps": [
      "Faire cuire les pâtes dans une grande casserole d'eau bouillante salée.",
      "Faire revenir les lardons à la poêle sans ajouter de matière grasse.",
      "Mélanger les œufs et le parmesan râpé dans un bol.",
      "Égoutter les pâtes, ajouter les lardons puis le mélange d'œufs hors du feu."
    ],
    "cook_time": "15 min",
    "embedding": [0.0124, -0.0521, 0.0891, 0.0032]
  }
]
```

#### Exemple de Réponse
```json
{
  "status": "success",
  "message": "1 recettes insérées avec succès dans ChromaDB."
}
```

---

### 2. Génération sous Contraintes (« Frigo Vide »)
- **Route** : `POST /api/v1/generate`
- **Rôle** : Reçoit une liste d'ingrédients bruts et génère une recette valide sous format JSON sans inventer d'ingrédients incohérents. Enregistre également l'empreinte carbone générée par l'inférence.

#### Exemple de Requête (`POST`)
```json
{
  "ingredients": [
    "œufs",
    "tomates",
    "oignon"
  ],
  "dietary_constraints": [
    "végétarien"
  ]
}
```

#### Exemple de Réponse
```json
{
  "status": "success",
  "recipe": {
    "title": "Poêlée de tomates aux œufs et oignons",
    "cook_time": "15 min",
    "used_ingredients": [
      "œufs",
      "tomates",
      "oignon"
    ],
    "steps": [
      "Émincer l'oignon et le faire revenir dans une poêle avec un filet d'huile d'olive.",
      "Couper les tomates en dés et les ajouter aux oignons.",
      "Laisser mijoter à feu moyen pendant 8 minutes.",
      "Casser les œufs directement sur le mélange et laisser cuire jusqu'à ce que les blancs soient pris."
    ],
    "emissions_kgco2eq": 0.00003851635342786505
  }
}
```

---

### 3. Agent Conversationnel RAG & Chatbot
- **Route** : `POST /api/v1/chat`
- **Rôle** : Permet à l'utilisateur de poser des questions sur une recette ou une substitution d'ingrédient. L'API extrait les contextes les plus pertinents depuis ChromaDB, maintient l'historique de la session et renvoie une réponse sourcée.

#### Exemple de Requête (`POST`)
```json
{
  "message": "Par quoi puis-je remplacer le beurre si je veux alléger la recette ?",
  "history": [
    {
      "role": "user",
      "content": "Comment réussir une sauce crémeuse pour mes pâtes ?"
    },
    {
      "role": "assistant",
      "content": "Tu peux utiliser une base de fromage frais ou de crème avec un peu d'eau de cuisson des pâtes."
    }
  ]
}
```

#### Exemple de Réponse
```json
{
  "status": "success",
  "data": {
    "response": "Pour remplacer le beurre et alléger votre recette, vous pouvez utiliser du fromage blanc 0% ou du yaourt grec. Pour les sauces, un peu d'eau de cuisson des pâtes liée avec une touche de fromage frais fonctionne aussi très bien.",
    "sources": [
      {
        "title": "Pâtes Carbonara Traditionnelles",
        "url": "https://www.marmiton.org/recettes/recette_pates-carbonara_12345.aspx"
      }
    ],
    "emissions_kgco2eq": 0.00002148102391823901
  }
}
```

---

## 📊 Suivi Environnemental (CodeCarbon)

Chaque appel aux fonctions de génération ou de RAG enregistre automatiquement la consommation d'énergie et l'estimation des émissions de CO2. Les métriques cumulées sont stockées à la racine dans le fichier `emissions.csv`.
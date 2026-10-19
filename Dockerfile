# Image Python officielle légère
FROM python:3.11-slim

# Évite l'écriture de fichiers .pyc et force l'affichage direct des logs Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Répertoire de travail dans le conteneur
WORKDIR /app

# Installation des dépendances système nécessaires (ex. compilateurs pour CodeCarbon ou ChromaDB)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copie et installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du reste du code de l'application
COPY . .

# Exposer le port de l'API FastAPI
EXPOSE 8080

# Commande de lancement de l'API avec Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
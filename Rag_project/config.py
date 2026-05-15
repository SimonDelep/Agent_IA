import os
from pathlib import Path
from dotenv import load_dotenv

# Charge les variables locales.
load_dotenv("dev.env")


# ==============================
# Azure OpenAI
# ==============================

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

# Noms des deployments Azure, pas noms abstraits des modèles
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
AZURE_OPENAI_CHAT_DEPLOYMENT = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")


# ==============================
# ChromaDB
# ==============================

CHROMA_PATH = os.getenv("CHROMA_PATH", "./db/chroma_store")
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "nordtrail_service_client")


# ==============================
# Documents et RAG
# ==============================

ROOT_DIR = Path(__file__).resolve().parent

DOCUMENTS_PATH = Path(os.getenv("DOCUMENTS_PATH", ROOT_DIR / "documents"))

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
TOP_K = int(os.getenv("TOP_K", "5"))


# ==============================
# Validation de configuration
# ==============================

def validate_config():
    missing = []

    if not AZURE_OPENAI_API_KEY:
        missing.append("AZURE_OPENAI_API_KEY")

    if not AZURE_OPENAI_ENDPOINT:
        missing.append("AZURE_OPENAI_ENDPOINT")

    if not AZURE_OPENAI_EMBEDDING_DEPLOYMENT:
        missing.append("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

    if not AZURE_OPENAI_CHAT_DEPLOYMENT:
        missing.append("AZURE_OPENAI_CHAT_DEPLOYMENT")

    if missing:
        raise ValueError(
            "Variables d'environnement manquantes dans dev.env : "
            + ", ".join(missing)
        )

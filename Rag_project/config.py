import os
from dotenv import load_dotenv

load_dotenv("dev.env")

# Azure OpenAI configuration
# You should set at least:
# - AZURE_OPENAI_API_KEY
# - AZURE_OPENAI_ENDPOINT  (e.g. https://your-resource-name.openai.azure.com/)
# - AZURE_OPENAI_API_VERSION (optional, has a default below)
OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

# These should be the *deployment names* of your Azure OpenAI models
OPENAI_EMBEDDING_MODEL = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large")
OPENAI_CHAT_MODEL = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4.1-mini")

CHROMA_PATH = os.getenv("CHROMA_PATH", "./db/chroma_store")
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "notes_cours_ai")

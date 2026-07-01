from typing import Final
import os

# Reuse existing config/settings.py to keep identical behavior while exposing a clean API.
from config import settings as legacy_settings

GEMINI_API_KEY: Final = os.getenv("GEMINI_API_KEY") or legacy_settings.GEMINI_API_KEY
QDRANT_URL: Final = os.getenv("QDRANT_URL") or legacy_settings.QDRANT_URL
QDRANT_API_KEY: Final = os.getenv("QDRANT_API_KEY") or legacy_settings.QDRANT_API_KEY
LLM_MODEL: Final = os.getenv("LLM_MODEL", legacy_settings.LLM_MODEL)
EMBEDDING_MODEL: Final = os.getenv("EMBEDDING_MODEL", legacy_settings.EMBEDDING_MODEL)
TOP_K: Final = int(os.getenv("TOP_K", legacy_settings.TOP_K))
COLLECTION_NAME: Final = os.getenv("COLLECTION_NAME", legacy_settings.COLLECTION_NAME)


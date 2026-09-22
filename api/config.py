"""Central configuration for the MooFile backend."""
import os

# Project root (the directory that contains this api/ package)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Data root: db/<db_id>/ holds each database subdirectory
DB_DIR = os.path.join(BASE_DIR, "db")

# Legacy upload root used by databases created before uploads moved in-db.
LEGACY_UPLOAD_DIR = os.path.join(DB_DIR, "_uploads")

# Local embedding model (offline, 384 dims, Chinese + multilingual)
MODELS_DIR = os.path.join(BASE_DIR, "models", "sentence-transformers")
MODEL_PATH = os.path.join(
    MODELS_DIR,
    "paraphrase-multilingual-MiniLM-L12-v2",
)
EMBEDDING_DIMS = 384

# Default vectorization parameters
DEFAULT_CHUNK_SIZE = 500
DEFAULT_OVERLAP = 20
DEFAULT_TOP_K = 10
DEFAULT_SIMILARITY_THRESHOLD = 0.3

# Server
HOST = "127.0.0.1"
PORT = 8888

# Storage quota for /api/system/storage (GB)
STORAGE_QUOTA_GB = 5.0

# Allowed upload extensions
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md", ".markdown", ".docx", ".doc",
                      ".pptx", ".ppt", ".xlsx", ".csv", ".html", ".htm"}
MAX_UPLOAD_MB = 50

os.makedirs(DB_DIR, exist_ok=True)

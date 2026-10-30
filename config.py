"""Central configuration for the Presidency University campus guide."""
from pathlib import Path
import os
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")
KNOWLEDGE_DIR = ROOT / "knowledge_base"
IMAGE_DIR = ROOT / "picture"
DATA_DIR = ROOT / "data"
CHROMA_DIR = DATA_DIR / "chroma_db"
UPLOAD_DIR = DATA_DIR / "uploads"
METADATA_FILE = DATA_DIR / "image_metadata.json"
EVALUATION_FILE = DATA_DIR / "evaluation_questions.json"
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "presidency_campus_guide")
CHUNK_WORDS = int(os.getenv("CHUNK_WORDS", "200"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "20"))
TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "4"))

"""Configuration management for the KG-RAG application."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration."""
    
    # Project paths
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    RAW_DATA_DIR = DATA_DIR / "raw"
    PROCESSED_DATA_DIR = DATA_DIR / "processed"
    RDF_DATA_DIR = DATA_DIR / "rdf"
    ONTOLOGY_DIR = DATA_DIR / "ontology"
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    
    # Model configurations
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    LLM_MODEL = "gpt-3.5-turbo"  # Can be changed to groq models
    
    # Knowledge Graph settings
    KG_NAMESPACE = "http://example.org/techcorp#"
    ONTOLOGY_FILE = ONTOLOGY_DIR / "techcorp_ontology.ttl"
    
    # Vector store settings
    VECTOR_STORE_DIM = 384  # Dimension for MiniLM model
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist."""
        for dir_path in [cls.DATA_DIR, cls.RAW_DATA_DIR, cls.PROCESSED_DATA_DIR, 
                        cls.RDF_DATA_DIR, cls.ONTOLOGY_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)
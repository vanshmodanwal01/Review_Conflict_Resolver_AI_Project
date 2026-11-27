"""Vector Embedding Service supporting Sentence Transformers and Deterministic Fallback"""
import math
import hashlib
from typing import List, Optional
from backend.core.config import settings
from backend.core.logging import logger

_st_model = None

class EmbeddingService:
    """
    Generates 384-dimensional vector embeddings for review texts and aspect clauses.
    
    Modes:
    1. Semantic Embedding (USE_LOCAL_TRANSFORMERS=True):
       Uses Hugging Face Sentence Transformers ('all-MiniLM-L6-v2') to produce
       true semantic embeddings capturing contextual meaning and synonymy.
    2. Deterministic Hash Projection Fallback (USE_LOCAL_TRANSFORMERS=False):
       Uses multi-seed SHA-256 hashing to produce normalized 384-d pseudo-vectors.
       This provides sub-millisecond offline execution for development without
       requiring heavy deep learning model downloads or PyTorch initialization.
    """
    def __init__(self, model_name: str = settings.EMBEDDING_MODEL_NAME, dimension: int = settings.VECTOR_DIMENSION):
        self.model_name = model_name
        self.dimension = dimension

    def _get_st_model(self):
        global _st_model
        if not getattr(settings, "USE_LOCAL_TRANSFORMERS", False):
            return False
        if _st_model is None:
            try:
                from sentence_transformers import SentenceTransformer
                try:
                    _st_model = SentenceTransformer(self.model_name, local_files_only=True)
                except Exception:
                    _st_model = SentenceTransformer(self.model_name)
                logger.info(f"Loaded SentenceTransformer semantic model '{self.model_name}'.")
            except Exception as e:
                logger.warning(f"Could not load SentenceTransformer: {e}")
                _st_model = False
        return _st_model

    def embed_text(self, text: str) -> List[float]:
        """Returns normalized 384-d vector for given text."""
        cleaned = text.strip()
        model = self._get_st_model()
        if model:
            try:
                vec = model.encode(cleaned, normalize_embeddings=True)
                return [round(float(x), 6) for x in vec]
            except Exception as e:
                logger.error(f"Error encoding with SentenceTransformer: {e}")

        # Deterministic 384-dimensional normalized hash projection fallback
        return self._deterministic_vector(cleaned)

    def _deterministic_vector(self, text: str) -> List[float]:
        """
        Creates a normalized 384-dimensional deterministic vector using multi-seed
        SHA-256 hashing. Note: This is an offline pseudo-vector projection, NOT a
        semantic embedding.
        """
        vec = []
        for i in range(self.dimension):
            h = hashlib.sha256(f"{text}:{i}".encode('utf-8')).hexdigest()
            val = (int(h[:8], 16) / 0xFFFFFFFF) * 2.0 - 1.0
            vec.append(val)
        
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [round(x / norm, 6) for x in vec]
        return vec

    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculates cosine similarity between two float vectors."""
        if len(vec1) != len(vec2) or not vec1:
            return 0.0
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return max(-1.0, min(1.0, dot / (norm1 * norm2)))

embedding_service = EmbeddingService()

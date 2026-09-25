"""
Embedding backend for the recommendation engine.

Tries Sentence-BERT (semantic embeddings) first. If sentence-transformers
isn't installed / model can't be downloaded (e.g. offline dev machine),
falls back to TF-IDF so the API still boots and works end to end.
"""
from __future__ import annotations

import numpy as np

_USE_SBERT = True
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    _USE_SBERT = False

from sklearn.feature_extraction.text import TfidfVectorizer

_MODEL_NAME = "all-MiniLM-L6-v2"


class EmbeddingBackend:
    def __init__(self):
        self.mode = None
        self._sbert_model = None
        self._tfidf = None

        if _USE_SBERT:
            try:
                self._sbert_model = SentenceTransformer(_MODEL_NAME)
                self.mode = "sbert"
            except Exception:
                self.mode = None

        if self.mode is None:
            self._tfidf = TfidfVectorizer(max_features=5000, stop_words="english")
            self.mode = "tfidf"

    def fit_transform(self, texts: list[str]) -> np.ndarray:
        if self.mode == "sbert":
            embeddings = self._sbert_model.encode(
                texts, show_progress_bar=False, normalize_embeddings=True
            )
            return np.asarray(embeddings, dtype="float32")
        else:
            matrix = self._tfidf.fit_transform(texts).toarray().astype("float32")
            norms = np.linalg.norm(matrix, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            return matrix / norms

    def transform(self, texts: list[str]) -> np.ndarray:
        if self.mode == "sbert":
            embeddings = self._sbert_model.encode(
                texts, show_progress_bar=False, normalize_embeddings=True
            )
            return np.asarray(embeddings, dtype="float32")
        else:
            matrix = self._tfidf.transform(texts).toarray().astype("float32")
            norms = np.linalg.norm(matrix, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            return matrix / norms

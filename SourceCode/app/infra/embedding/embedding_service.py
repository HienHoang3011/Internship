from app.infra.embedding.base import BaseEmbeddingService
from app.infra.embedding.gemini_embedding import GeminiEmbeddingService
from app.infra.embedding.vidense_embedding import VidenseEmbedding
from typing import Any


def _serialize_embedding(obj: Any) -> Any:
    """Ensure the embedding is a JSON/BSON serializable Python type (list of floats).

    Supports torch.Tensor, numpy.ndarray, lists of those, or already-serializable lists.
    """
    try:
        import torch
    except Exception:
        torch = None

    try:
        import numpy as _np
    except Exception:
        _np = None

    # Torch tensor
    if torch is not None and isinstance(obj, torch.Tensor):
        arr = obj.detach().cpu().numpy()
        # If it's shape (1, dim) return 1D list
        if getattr(arr, 'ndim', None) == 2 and arr.shape[0] == 1:
            return arr[0].tolist()
        return arr.tolist()

    # Numpy array
    if _np is not None and isinstance(obj, _np.ndarray):
        arr = obj
        if getattr(arr, 'ndim', None) == 2 and arr.shape[0] == 1:
            return arr[0].tolist()
        return arr.tolist()

    # List/tuple - recursively serialize elements
    if isinstance(obj, (list, tuple)):
        return [_serialize_embedding(x) for x in obj]

    # Fallback: return as-is (could be already a list of floats)
    return obj


class EmbeddingService(BaseEmbeddingService):
    def __init__(self, provider: str = "gemini"):
        """Khởi tạo Embedding Service dựa trên tên provider."""
        self.provider_name = provider.lower()
        self.client = self._initialize_provider()

    def _initialize_provider(self):
        if self.provider_name == "gemini":
            return GeminiEmbeddingService()
        elif self.provider_name == "vidense":
            return VidenseEmbedding()
        else:
            raise ValueError(f"Unsupported embedding provider: {self.provider_name}")

    def embed(self, text: str):
        result = self.client.embed(text)
        return _serialize_embedding(result)

    def embed_batch(self, texts: list):
        result = self.client.embed_batch(texts)
        return _serialize_embedding(result)

    def get_name(self):
        return self.client.get_name()

    def embed_query(self, text: str):
        if hasattr(self.client, 'embed_query'):
            result = self.client.embed_query(text)
        else:
            result = self.client.embed(text)
        return _serialize_embedding(result)

    def embed_document(self, text: str):
        if hasattr(self.client, 'embed_document'):
            result = self.client.embed_document(text)
        else:
            result = self.client.embed(text)
        return _serialize_embedding(result)
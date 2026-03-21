from app.services.embedding.base import BaseEmbeddingService
from app.services.embedding.gemini_embedding import GeminiEmbeddingService
from app.services.embedding.vidense_embedding import VidenseEmbedding

class EmbeddingService(BaseEmbeddingService):
    def __init__(self, provider: str = "gemini"):
        """
        Khởi tạo Embedding Service dựa trên tên provider.
        """
        self.provider_name = provider.lower()
        self.client = self._initialize_provider()

    def _initialize_provider(self):
        # Khởi tạo class con tương ứng với provider
        if self.provider_name == "gemini":
            return GeminiEmbeddingService()
        elif self.provider_name == "vidense":
            return VidenseEmbedding()
        else:
            raise ValueError(f"Unsupported embedding provider: {self.provider_name}")

    def embed(self, text: str):
        return self.client.embed(text)

    def embed_batch(self, texts: list):
        return self.client.embed_batch(texts)

    def get_name(self):
        return self.client.get_name()

    def embed_query(self, text: str):
        # Kiểm tra xem class con có hỗ trợ hàm này không (Vidense hiện không có hàm này)
        if hasattr(self.client, 'embed_query'):
            return self.client.embed_query(text)
        # Nếu không có, fallback về hàm embed mặc định
        return self.client.embed(text)

    def embed_document(self, text: str):
        if hasattr(self.client, 'embed_document'):
            return self.client.embed_document(text)
        return self.client.embed(text)
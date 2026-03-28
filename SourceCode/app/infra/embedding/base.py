from abc import ABC, abstractmethod
class BaseEmbeddingService(ABC):
    def __init__(self, embedding_model):
        self.embedding_model = embedding_model

    @abstractmethod
    def get_name(self):
        pass
    
    @abstractmethod
    def embed(self, text):
        pass
    @abstractmethod
    def embed_batch(self, texts):
        pass
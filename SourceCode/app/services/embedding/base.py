class BaseEmbeddingService:
    def __init__(self, embedding_model):
        self.embedding_model = embedding_model

    def get_name(self):
        return self.embedding_model.__class__.__name__
    def embed(self, text):
        raise NotImplementedError("Subclasses must implement the embed method.")
    def embed_batch(self, texts):
        raise NotImplementedError("Subclasses must implement the embed_batch method.")
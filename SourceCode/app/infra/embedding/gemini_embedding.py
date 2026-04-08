from app.infra.embedding.base import BaseEmbeddingService
from google import genai
import os
from dotenv import load_dotenv
load_dotenv(override = True)

class GeminiEmbeddingService(BaseEmbeddingService):
    def __init__(self):
        try:
            genai_client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
            self.client = genai_client
        except Exception as e:
            print(f"Error initializing Gemini client: {e}")
    def embed(self, text):
        result = self.client.models.embed_content(
            model = "gemini-embedding-001",
            contents=[text]
        )
        return result.embeddings[0].values
    def embed_batch(self, texts):
        result = self.client.models.embed_content(
            model = "gemini-embedding-001",
            contents=texts
        )
        return [embedding.values for embedding in result.embeddings]
    def get_name(self):
        return "gemini"
    def embed_with_task(self, text, task_type = "SEMANTIC_SIMILARITY"):
        """
        task_type: Task type for embedding. Options:
            - "RETRIEVAL_DOCUMENT": For documents to be retrieved
            - "RETRIEVAL_QUERY": For search queries
            - "SEMANTIC_SIMILARITY": For similarity comparison
            - "CLASSIFICATION": For text classification
            - "CLUSTERING": For text clustering

        """
        result = self.client.models.embed_content(
            model = "gemini-embedding-001",
            contents=[text],
            config={"task_type": task_type},
        )
        return result.embeddings[0].values
    
    def embed_query(self, text):
        return self.embed_with_task(text, task_type="RETRIEVAL_QUERY")
    def embed_document(self, text):
        return self.embed_with_task(text, task_type="RETRIEVAL_DOCUMENT")
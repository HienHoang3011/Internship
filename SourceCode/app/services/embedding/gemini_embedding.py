from app.services.embedding.embedding_service import BaseEmbeddingService
from google import genai
import os
from dotenv import load_dotenv
load_dotenv(override = True)

class GeminiEmbeddingService(BaseEmbeddingService):
    def __init__(self):
        genai_clent = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_text_splitters import MarkdownHeaderTextSplitter
from embedding.embedding_service import EmbeddingService
import numpy as np

def cosine_similarity(vec_a, vec_b):
    if np.linalg.norm(vec_a) == 0 or np.linalg.norm(vec_b) == 0:
        return 0.0
    return np.dot(vec_a, vec_b) / (np.linalg.norm(vec_a) * np.linalg.norm(vec_b))

class ChunkingService:
    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service
        
    def split_by_characters(self, text, chunk_size: int = 1000, chunk_overlap: int = 200):
        recursive_textsplitter = RecursiveCharacterTextSplitter(
            chunk_size = chunk_size,
            chunk_overlap = chunk_overlap,
            is_separator_regex= True,
            separators = ["\n\n", "\n", "."]
        )
        split_text = recursive_textsplitter.split_text(text)
        return split_text
    
    def split_markdown(self, text):
        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
            ("####", "Header 4"),
            ("#####", "Header 5")
        ]
        markdown_spliter = MarkdownHeaderTextSplitter(headers_to_split_on= headers_to_split_on)
        md_text_split = markdown_spliter.split_text(text)
        return md_text_split
    
    def semantic_split(self, text):
        sentences = text.split(". ")
        sentence_embeddings = [self.embedding_service.get_embedding(sentence) for sentence in sentences]
        similarity_threshold = 0.8
        chunks = []
        current_chunk = []
        for i, sentence in enumerate(sentences):
            if not current_chunk:
                current_chunk.append(sentence)
            else:
                last_sentence_embedding = self.embedding_service.get_embedding(current_chunk[-1])
                similarity = cosine_similarity(last_sentence_embedding, sentence_embeddings[i])
                if similarity > similarity_threshold:
                    current_chunk.append(sentence)
                else:
                    chunks.append(". ".join(current_chunk))
                    current_chunk = [sentence]
        if current_chunk:
            chunks.append(". ".join(current_chunk))
        return chunks
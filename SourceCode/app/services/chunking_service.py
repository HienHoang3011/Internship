from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_text_splitters import MarkdownHeaderTextSplitter
from app.infra.embedding.embedding_service import EmbeddingService
import numpy as np  
import re
 
def _get_markdown_header_string(metadata):
    headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
            ("####", "Header 4"),
            ("#####", "Header 5")
        ]
    """Constructs the markdown header string from metadata."""
    if not metadata:
        return ""
    # Note: headers_to_split_on is global, so it needs to be accessible.
    header_info = []
    # Iterate through headers from H1 to H5 to find the deepest one
    # (headers_to_split_on should be defined globally before this function or passed)
    for prefix, key in headers_to_split_on:
        if key in metadata:
            header_info.append((prefix, metadata[key].strip()))

    if header_info:
        # Return the deepest (last) header found, e.g., '## Subheader'
        return f"{header_info[-1][0]}{header_info[-1][1]}"
    return ""

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
        """
        Chia văn bản markdown thành các phần dựa trên các header #, ##, ###,...
        Nếu một phần quá ngắn, gộp vào chunk trước đó.
        Sau đó, chia nhỏ các phần còn lại bằng RecursiveCharacterTextSplitter với separators '\n\n' và '\n'.
        Nếu một phần sau khi chia vẫn quá dài, chia nhỏ nó ra tiếp.
        Thêm header vào đầu mỗi semantic chunk.

        Args:
            text (str): Chuỗi markdown cần chia.

        Returns:
            list[str]: Một danh sách các chuỗi văn bản đã được chia tách.
        """
        # Remove only the first H1 block (header level '#') then use
        # MarkdownHeaderTextSplitter for the rest.
        if not text:
            return []

        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
            ("####", "Header 4"),
            ("#####", "Header 5")
        ]

        header_regex = re.compile(r'(?m)^(#{1,5})\s*(.*)\s*$')
        matches = list(header_regex.finditer(text))

        # Find first H1 and remove its block (from that H1 until the next H1)
        h1_indices = [i for i, m in enumerate(matches) if len(m.group(1)) == 1]
        if h1_indices:
            first_i = h1_indices[0]
            start = matches[first_i].start()
            # keep leading content before first H1
            leading = text[:start]
            next_start = None
            for j in range(first_i + 1, len(matches)):
                if len(matches[j].group(1)) == 1:
                    next_start = matches[j].start()
                    break
            rest = text[next_start:] if next_start is not None else ""
            text = (leading + "\n" + rest).strip()

        # Use the MarkdownHeaderTextSplitter for the pruned text
        markdown_spliter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
        docs = markdown_spliter.split_text(text)

        # Combine headers and content, merging short content sections
        processed_docs_with_headers = []  # Stores tuples of (full_header_string, content_text)
        short_content_threshold = 50

        for doc in docs:
            header_str = _get_markdown_header_string(doc.metadata)
            content = doc.page_content.strip()

            if len(content) < short_content_threshold and processed_docs_with_headers:
                merged_segment = f"{header_str}\n\n{content}" if header_str else content
                processed_docs_with_headers[-1] = (
                    processed_docs_with_headers[-1][0],
                    (processed_docs_with_headers[-1][1] + "\n\n" + merged_segment).strip()
                )
            else:
                processed_docs_with_headers.append((header_str, content))

        # Convert processed_docs_with_headers into final chunks (header + content)
        final_chunks = []
        for header, content in processed_docs_with_headers:
            header = (header or "").strip()
            content = (content or "").strip()
            if header and content:
                final_chunks.append(f"{header}\n\n{content}")
            elif content:
                final_chunks.append(content)
            elif header:
                final_chunks.append(header)

        return final_chunks
    
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
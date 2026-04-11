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
        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
            ("####", "Header 4"),
            ("#####", "Header 5")
        ]
        markdown_spliter = MarkdownHeaderTextSplitter(headers_to_split_on= headers_to_split_on)
    
        if not text:
            return []

        # Use the pre-defined markdown_splitter from SHueLbuVqlVb
        docs =markdown_spliter.split_text(text)

        # Step 1: Combine headers and content, merging short content sections
        processed_docs_with_headers = [] # Stores tuples of (full_header_string, content_text)
        short_content_threshold = 50 # Threshold for content length to trigger merging

        for doc in docs:
            header_str = _get_markdown_header_string(doc.metadata)
            content = doc.page_content.strip()

            # If the content is too short and there's a previous processed chunk, merge them.
            # Otherwise, add as a new chunk.
            if len(content) < short_content_threshold and processed_docs_with_headers:
                # Append content to the previous chunk's content.
                # If the current doc has a header, prepend it to its content before merging.
                merged_segment = f"{header_str}\n\n{content}" if header_str else content
                processed_docs_with_headers[-1] = (
                    processed_docs_with_headers[-1][0], # Keep original header of the prev chunk
                    processed_docs_with_headers[-1][1] + "\n\n" + merged_segment
                )
            else:
                processed_docs_with_headers.append((header_str, content))

        # Convert processed_docs_with_headers into the initial_h_chunks (full strings)
        initial_h_chunks = []
        for header, content in processed_docs_with_headers:
            if header:
                initial_h_chunks.append(f"{header}\n\n{content}")
            else:
                initial_h_chunks.append(content)

        intermediate_chunks_with_headers = []
        # Step 2: Chia nhỏ các chunk còn lại bằng split_by_characters

        for h_chunk in initial_h_chunks:
            stripped_h_chunk = h_chunk.strip()
            if not stripped_h_chunk:
                continue

            # Extract the header string and content for splitting
            header_match = re.match(r'^(#+)\s*(.*?)(?:\n|$)', stripped_h_chunk)
            current_chunk_header = ""
            content_for_recursive_split = stripped_h_chunk

            if header_match:
                header_prefix = header_match.group(1)
                header_text = header_match.group(2).strip()
                current_chunk_header = f"{header_prefix} {header_text}".strip()
                content_for_recursive_split = re.sub(r'^(#+)\s*(.*?)(?:\n|\n\n|$)', '', stripped_h_chunk, count=1).strip()

            # If no explicit header was found at the beginning, the whole chunk is content
            if not content_for_recursive_split and current_chunk_header: # Edge case: chunk was just a header
                intermediate_chunks_with_headers.append((current_chunk_header, ""))
                continue
            elif not content_for_recursive_split: # Empty chunk
                continue


            recursively_split_contents = self.split_by_characters(content_for_recursive_split, chunk_size=2000, chunk_overlap=0)

            for chunk_content in recursively_split_contents:
                intermediate_chunks_with_headers.append((current_chunk_header, chunk_content.strip()))


        final_chunks = []
        # Step 3: Apply further splitting if a part is still too long
        semantic_threshold = 1000 # Threshold to apply further splitting

        for header, i_chunk_content in intermediate_chunks_with_headers:
            stripped_i_chunk_content = i_chunk_content.strip()
            if not stripped_i_chunk_content:
                # If the content part is empty, and it had a header, just include the header.
                # This handles cases where a header might be followed by only whitespace or very little content
                # that was stripped.
                if header:
                    final_chunks.append(header)
                continue

            if len(stripped_i_chunk_content) > semantic_threshold:
                print(f"Chunk content too long ({len(stripped_i_chunk_content)} chars), applying further splitting.")
                try:
                    sub_chunks_from_content = self.split_by_characters(stripped_i_chunk_content, chunk_size=500, chunk_overlap=100)
                    print(f"  Initially split into {len(sub_chunks_from_content)} sub-chunks.")

                    if sub_chunks_from_content:
                        for sc in sub_chunks_from_content:
                            if header:
                                final_chunks.append(f"{header}\n\n{sc.strip()}")
                            else:
                                final_chunks.append(sc.strip())
                    elif header: # If no sub_chunks from content but there was a header
                        final_chunks.append(header)


                except Exception as e:
                    print(f"  Error during further splitting: {e}. Adding original chunk.")
                    if header:
                        final_chunks.append(f"{header}\n\n{stripped_i_chunk_content}")
                    else:
                        final_chunks.append(stripped_i_chunk_content)
            else:
                if header:
                    final_chunks.append(f"{header}\n\n{stripped_i_chunk_content}")
                else:
                    final_chunks.append(stripped_i_chunk_content)

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
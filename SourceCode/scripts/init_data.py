import os
import sys
import uuid
from pathlib import Path
from dotenv import load_dotenv
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.utils.cleaner_helpers import clean_text
from app.services.chunking_service import ChunkingService
from app.infra.embedding.embedding_service import EmbeddingService
from app.infra.mongodb_service import MongoDBService

load_dotenv(override=True)

def extract_headers_and_content(chunk_str):
    """
    Tách header và content từ một chunk string.
    Dựa vào ChunkingService, nó thường nối header và content lại bằng '\n\n'.
    """
    headers = []
    content = chunk_str
    
    # Kiểm tra dòng đầu tiên xem có phải là Markdown header không
    lines = chunk_str.strip().split('\n')
    if lines and lines[0].startswith('#'):
        headers.append(lines[0].strip())
        content = '\n'.join(lines[1:]).strip()
    
    return headers, content

def handle_data(file_path, chunking_service, embedding_service):
    """
    Xử lý một file:
    1. Đọc nội dung
    2. Clean text
    3. Split thành các chunk
    4. Gắn UUID, tách headers, tính embedding cho từng chunk
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"Lỗi khi đọc file {file_path}: {e}")
        return []
    
    # 1. Làm sạch dữ liệu
    cleaned_text = clean_text(text)
    
    # 2. Chunking
    chunks = chunking_service.split_markdown(cleaned_text)
    
    # 3. Embedding và chuẩn bị documents
    processed_chunks = []
    for chunk in chunks:
        # Tách header và content
        headers, content = extract_headers_and_content(chunk)
        
        # Bỏ qua các chunk rỗng sau khi làm sạch
        if not content.strip():
            continue
            
        # Nội dung dùng để embed: headers + content (chính là chuỗi chunk ban đầu)
        text_to_embed = chunk 
        
        try:
            # Gọi embedding service (sử dụng embed_document để tối ưu retrieval)
            embedding_vector = embedding_service.embed_document(text_to_embed)
            
            doc = {
                "uuid": str(uuid.uuid4()),
                "headers": headers,
                "content": content,
                "embedding": embedding_vector,
                "file_source": os.path.basename(file_path)
            }
            processed_chunks.append(doc)
        except Exception as e:
            print(f"Lỗi khi tính embedding cho chunk: {e}")
            
    return processed_chunks

def main():
    print("Khởi tạo dịch vụ...")
    # Khởi tạo các services
    embedding_service = EmbeddingService(provider="vidense")
    chunking_service = ChunkingService(embedding_service)
    mongo_service = MongoDBService()
    
    collection_name = os.getenv("MONGODB_COLLECTION", "knowledge_base")
    
    data_dir = Path(__file__).resolve().parent.parent / "data"
    
    if not data_dir.exists():
        print(f"Thư mục {data_dir} không tồn tại!")
        return
        
    all_documents = []
    
    # Duyệt qua các file markdown trong thư mục data
    print(f"Bắt đầu duyệt các file trong {data_dir}...")
    for filename in os.listdir(data_dir):
        if filename.endswith(".md") or filename.endswith(".txt"):
            file_path = data_dir / filename
            print(f"Đang xử lý file: {filename}...")
            
            # Xử lý data
            processed_chunks = handle_data(file_path, chunking_service, embedding_service)
            all_documents.extend(processed_chunks)
            print(f"  -> Trích xuất được {len(processed_chunks)} chunks hợp lệ.")
                
    if all_documents:
        print(f"\nĐang thêm tổng cộng {len(all_documents)} chunks vào MongoDB ({collection_name})...")
        try:
            inserted_ids = mongo_service.insert_many(collection_name, all_documents)
            print(f"Hoàn tất! Đã thêm thành công {len(inserted_ids)} records vào CSDL.")
        except Exception as e:
            print(f"Lỗi khi thêm vào MongoDB: {e}")
    else:
        print("Không có dữ liệu nào được trích xuất.")

if __name__ == "__main__":
    main()

import os
import json
from typing import Any, Dict, List
from dotenv import load_dotenv
from pymongo import MongoClient
from langchain_core.tools import tool
from app.infra.embedding.embedding_service import EmbeddingService

load_dotenv(override=True)

_mongo_uri = os.getenv("MONGODB_URI") or os.getenv("MONGODB_URL")
_mongo_db_name = os.getenv("MONGODB_DATABASE")
_mongo_collection_name = os.getenv("MONGODB_COLLECTION")

if _mongo_uri and _mongo_db_name and _mongo_collection_name:
    mongo_client = MongoClient(_mongo_uri)
    mongo_db = mongo_client[_mongo_db_name]
    mongo_collection = mongo_db[_mongo_collection_name]
else:
    mongo_collection = None 

embedding_service = EmbeddingService(provider="gemini")

@tool
def search_knowledge_base(
    query: str, 
    vector_search_index: str = "default", 
    candidates: int = 10, 
    limit: int = 8
) -> str:
    """Công cụ tìm kiếm thông tin trong cơ sở tri thức (Vector Database nội bộ).
    
    Sử dụng công cụ này khi cần khai thác, tra cứu các tài liệu, hướng dẫn, 
    quy định hoặc dữ liệu đã lưu trữ trong hệ thống gốc theo ngữ cảnh của người dùng, 
    để việc đưa ra câu trả lời được chính xác, trúng đích hơn.
    
    Args:
        query (str): Câu lệnh truy vấn cần tìm kiếm (ví dụ: "chính sách đổi trả hàng là gì").
        vector_search_index (str, optional): Tên của index thiết lập tìm kiếm vector trên database. Mặc định: "default".
        candidates (int, optional): Số lượng vector lân cận sẽ xét. Càng cao càng chính xác nhưng chậm đi. Mặc định: 10.
        limit (int, optional): Số lượng kết quả tối đa đưa vào câu trả lời trả về. Mặc định: 8.
        
    Returns:
        str: Một chuỗi định dạng JSON chứa danh sách tài liệu khớp (bao gồm các trường: headers, content, summary).
             Nếu gặp lỗi (database connection, index...), sẽ trả về thông báo mô tả lỗi tương ứng.
    """
    if mongo_collection is None:
        return "Lỗi: Không thể kết nối cơ sở tri thức MongoDB do thiếu biến môi trường cấu hình."

    try:
        query_vector = embedding_service.embed(query)
        pipeline = [
            {
                "$vectorSearch": {
                    "index": vector_search_index,
                    "path": "embedding",
                    "queryVector": query_vector,
                    "numCandidates": candidates,
                    "limit": limit,
                }
            },
            {
                "$project": {
                    "_id": 0,       
                    "uuid": 0,      
                    "headers": 1,   
                    "content": 1,   
                    "summary": 1    
                }
            }
        ]
        
        cursor = mongo_collection.aggregate(pipeline)
        result_list = list(cursor)

        return json.dumps(result_list, ensure_ascii=False, indent=4)
        
    except Exception as e:
        return f"Đã xảy ra lỗi trong quá trình thực hiện search cơ sở tri thức: {str(e)}"
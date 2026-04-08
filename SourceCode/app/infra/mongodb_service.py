import os
import logging
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

load_dotenv(override=True)

# Cấu hình logging cơ bản
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class MongoDBService:
    """
    Service class để tương tác với MongoDB.
    Cung cấp các thao tác CRUD cơ bản và quản lý kết nối.
    """

    def __init__(self) -> None:
        """Khởi tạo kết nối MongoDB sử dụng các biến tham số môi trường."""
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        
        try:
            mongo_uri = os.getenv("MONGODB_URI")
            db_name = os.getenv("MONGODB_DATABASE")
            
            if not mongo_uri or not db_name:
                logger.warning("Vui lòng thiết lập MONGODB_URI và MONGODB_DATABASE trong file .env.")
                return

            self.client = MongoClient(mongo_uri)
            self.db = self.client[db_name]
            logger.info(f"Đã kết nối thành công tới database: {db_name}")
        except Exception as e:
            logger.error(f"Lỗi khi kết nối tới MongoDB: {e}")

    def get_collection(self, collection_name: str) -> Optional[Collection]:
        """Lấy một collection cụ thể từ database."""
        if self.db is not None:
            return self.db[collection_name]
        logger.error("Kết nối Database chưa được khởi tạo.")
        return None

    def insert_one(self, collection_name: str, document: Dict[str, Any]) -> Any:
        """Thêm một document vào collection."""
        collection = self.get_collection(collection_name)
        if collection is not None:
            result = collection.insert_one(document)
            return result.inserted_id
        return None

    def insert_many(self, collection_name: str, documents: List[Dict[str, Any]]) -> List[Any]:
        """Thêm nhiều document vào collection."""
        collection = self.get_collection(collection_name)
        if collection is not None:
            result = collection.insert_many(documents)
            return result.inserted_ids
        return []

    def find_one(self, collection_name: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Tìm một document khớp với điều kiện (query)."""
        collection = self.get_collection(collection_name)
        if collection is not None:
            return collection.find_one(query)
        return None

    def find_many(self, collection_name: str, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Tìm nhiều document khớp với điều kiện (query)."""
        if query is None:
            query = {}
        collection = self.get_collection(collection_name)
        if collection is not None:
            return list(collection.find(query))
        return []

    def update_one(self, collection_name: str, query: Dict[str, Any], update: Dict[str, Any]) -> int:
        """Cập nhật một document khớp với điều kiện (query)."""
        collection = self.get_collection(collection_name)
        if collection is not None:
            result = collection.update_one(query, update)
            return result.modified_count
        return 0

    def delete_one(self, collection_name: str, query: Dict[str, Any]) -> int:
        """Xóa một document khớp với điều kiện (query)."""
        collection = self.get_collection(collection_name)
        if collection is not None:
            result = collection.delete_one(query)
            return result.deleted_count
        return 0

    def delete_many(self, collection_name: str, query: Dict[str, Any]) -> int:
        """Xóa nhiều documents khớp với điều kiện (query)."""
        collection = self.get_collection(collection_name)
        if collection is not None:
            result = collection.delete_many(query)
            return result.deleted_count
        return 0

    def drop_collection(self, collection_name: str) -> None:
        """Xóa bỏ (Drop) một collection khỏi database."""
        if self.db is not None:
            self.db.drop_collection(collection_name)
            logger.info(f"Đã xóa collection: {collection_name}")
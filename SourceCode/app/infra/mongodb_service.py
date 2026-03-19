import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv(override = True)

class MongoDBService:
    def __init__(self):
        try:
            self.client = MongoClient(os.getenv("MONGODB_URI"))
            self.db = self.client[os.getenv("MONGODB_DATABASE")]
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
    def get_collection(self, collection_name):
        return self.db[collection_name]
    def insert_one(self, collection_name, document):
        collection = self.get_collection(collection_name)
        collection.insert_one(document)
    def insert_many(self, collection_name, documents):
        collection = self.get_collection(collection_name)
        collection.insert_many(documents)
    def find_one(self, collection_name, query):
        collection = self.get_collection(collection_name)
        return collection.find_one(query)
    def find_many(self, collection_name, query={}):
        collection = self.get_collection(collection_name)
        return list(collection.find(query))
    def update_one(self, collection_name, query, update):
        collection = self.get_collection(collection_name)
        collection.update_one(query, update)
    def delete_one(self, collection_name, query):
        collection = self.get_collection(collection_name)
        collection.delete_one(query)
    def delete_many(self, collection_name, query):
        collection = self.get_collection(collection_name)
        collection.delete_many(query)
    def drop_collection(self, collection_name):
        self.db.drop_collection(collection_name)
    
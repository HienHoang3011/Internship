from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from bson import ObjectId
import json
from app.infra.mongodb_service import MongoDBService

mongo_service = MongoDBService()

def convert_object_ids(doc):
    if doc and '_id' in doc:
        doc['id'] = str(doc['_id'])
        del doc['_id']
    return doc

class LessonListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        lessons = mongo_service.find_many("lessons")
        lessons = [convert_object_ids(l) for l in lessons]
        return Response(lessons)

    def post(self, request):
        if request.user.email != 'admin@gmail.com':
            return Response({"error": "Unauthorized"}, status=403)
        
        data = request.data
        inserted_id = mongo_service.insert_one("lessons", data)
        if inserted_id:
            data['id'] = str(inserted_id)
            if '_id' in data:
                del data['_id']
            return Response(data, status=201)
        return Response({"error": "Could not create lesson"}, status=400)

class LessonDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, pk):
        if request.user.email != 'admin@gmail.com':
            return Response({"error": "Unauthorized"}, status=403)
            
        try:
            query = {"_id": ObjectId(pk)}
            update = {"$set": request.data}
            modified = mongo_service.update_one("lessons", query, update)
            if modified:
                return Response({"status": "updated"})
            return Response({"error": "Not found or no changes"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    def delete(self, request, pk):
        if request.user.email != 'admin@gmail.com':
            return Response({"error": "Unauthorized"}, status=403)
            
        try:
            deleted = mongo_service.delete_one("lessons", {"_id": ObjectId(pk)})
            if deleted:
                return Response(status=204)
            return Response({"error": "Not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

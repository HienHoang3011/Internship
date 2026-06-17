from rest_framework import generics, permissions
from app.core.models import DiaryEntry
from .serializers import DiaryEntrySerializer

class DiaryEntryListCreateView(generics.ListCreateAPIView):
    serializer_class = DiaryEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DiaryEntry.objects.filter(user=self.request.user)

class DiaryEntryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DiaryEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DiaryEntry.objects.filter(user=self.request.user)

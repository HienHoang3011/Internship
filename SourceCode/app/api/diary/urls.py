from django.urls import path
from .views import DiaryEntryListCreateView, DiaryEntryDetailView

urlpatterns = [
    path('', DiaryEntryListCreateView.as_view(), name='diary-list-create'),
    path('<int:pk>/', DiaryEntryDetailView.as_view(), name='diary-detail'),
]

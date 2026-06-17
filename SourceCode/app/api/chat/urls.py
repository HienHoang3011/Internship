from django.urls import path
from .views import ChatSessionListCreateView, ChatSessionDetailView, ChatMessageCreateView

urlpatterns = [
    path('', ChatSessionListCreateView.as_view(), name='session-list-create'),
    path('<int:pk>/', ChatSessionDetailView.as_view(), name='session-detail'),
    path('<int:session_id>/messages/', ChatMessageCreateView.as_view(), name='message-create'),
]

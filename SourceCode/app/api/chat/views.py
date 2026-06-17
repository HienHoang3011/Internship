from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from app.core.models import ChatSession, ChatMessage
from .serializers import ChatSessionSerializer, ChatMessageSerializer
import requests
import os
from google import genai

class ChatSessionListCreateView(generics.ListCreateAPIView):
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ChatSessionDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)

class ChatMessageCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id):
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        text = request.data.get('text')
        
        if not text:
            return Response({'detail': 'Text is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 1. Save user message
        user_msg = ChatMessage.objects.create(session=session, sender='user', text=text)
        
        # Update session title if it's the first real message
        if session.messages.count() == 1 and "Cuộc trò chuyện mới" in session.title:
            try:
                client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=f'Dựa vào tin nhắn đầu tiên của người dùng: "{text}". Hãy tạo một tiêu đề cực kỳ ngắn gọn (tối đa 3-5 từ) tóm tắt bao quát chủ đề hoặc ý định của cuộc trò chuyện. Hãy đặt tên thật tự nhiên giống như cách AI tự đặt tên đoạn chat. Chú ý: Chỉ trả về duy nhất text tiêu đề, KHÔNG dùng dấu ngoặc kép, KHÔNG cần câu giới thiệu.'
                )
                session.title = response.text.strip().replace('"', '')
            except Exception as e:
                print(f"Error generating title with Gemini: {e}")
                session.title = text[:20] + "..." if len(text) > 20 else text
            session.save()
            
        # 2. Call external AI Agent API
        api_messages = []
        for msg in session.messages.order_by('created_at'):
            role = 'user' if msg.sender == 'user' else 'assistant'
            api_messages.append({"role": role, "content": msg.text})
            
        bot_text = "Xin lỗi, hiện tại máy chủ AI đang bận. Vui lòng thử lại sau."
        try:
            agent_url = os.environ.get("AGENT_API_URL", "http://localhost:8001/chat")
            agent_response = requests.post(
                agent_url,
                json={"messages": api_messages},
                timeout=30
            )
            if agent_response.status_code == 200:
                data = agent_response.json()
                if "response" in data:
                    bot_text = data["response"]
        except Exception as e:
            print(f"Error calling AI agent: {e}")
        
        # 3. Save Bot message
        bot_msg = ChatMessage.objects.create(session=session, sender='bot', text=bot_text)
        
        # 4. Return serialized data
        return Response({
            'user_message': ChatMessageSerializer(user_msg).data,
            'bot_message': ChatMessageSerializer(bot_msg).data,
            'session_title': session.title
        }, status=status.HTTP_201_CREATED)

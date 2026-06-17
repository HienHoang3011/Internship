from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
import os
from google import genai
import json

from app.core.models import Test, TestResult
from .serializers import TestSerializer, TestResultSerializer

class IsAdminUser(IsAuthenticated):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.email == 'admin@gmail.com')

class TestListCreateView(generics.ListCreateAPIView):
    serializer_class = TestSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [IsAuthenticated()]
        
    def get_queryset(self):
        return Test.objects.all()

class TestDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TestSerializer
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return Test.objects.all()

class TestResultListCreateView(generics.ListCreateAPIView):
    serializer_class = TestResultSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TestResult.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TestAnalyzeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, result_id):
        test_result = get_object_or_404(TestResult, id=result_id, user=request.user)
        test = test_result.test
        
        # Prepare context for AI
        answers_data = test_result.answers
        
        context = f"Người dùng đã làm bài kiểm tra: {test.name} ({test.type}).\n\nDanh sách câu trả lời:\n"
        for ans in answers_data:
            question = ans.get('question', '')
            answer = ans.get('answer', '')
            score = ans.get('score', '')
            if score != '':
                context += f"- Câu hỏi: {question}\n  Đáp án: {answer} (Điểm: {score})\n"
            else:
                context += f"- Câu hỏi: {question}\n  Đáp án: {answer}\n"
                
        if test_result.raw_result:
            context += "\nTổng điểm theo từng nhóm yếu tố:\n"
            for dim, score in test_result.raw_result.items():
                context += f"- {dim}: {score}\n"
                
        prompt = f"""
        Bạn là một chuyên gia tâm lý học. Dựa vào kết quả dưới đây của người dùng trong bài kiểm tra "{test.name}", hãy phân tích tính cách hoặc tình trạng tâm lý của họ một cách nhẹ nhàng, khoa học và thấu cảm.
        
        Nếu bài kiểm tra là DASS-21, hãy đối chiếu tổng điểm của họ với bảng phân loại lâm sàng (lưu ý điểm đã được nhân 2):
        - Trầm cảm: Bình thường (0-9), Nhẹ (10-13), Vừa (14-20), Nặng (21-27), Rất nặng (28+).
        - Lo âu: Bình thường (0-7), Nhẹ (8-9), Vừa (10-14), Nặng (15-19), Rất nặng (20+).
        - Stress: Bình thường (0-14), Nhẹ (15-18), Vừa (19-25), Nặng (26-33), Rất nặng (34+).
        
        Dữ liệu kết quả:
        {context}
        
        Vui lòng đưa ra nhận xét chi tiết, chỉ rõ mức độ cho từng khía cạnh và đưa ra lời khuyên hữu ích bằng tiếng Việt.
        """
        
        try:
            client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            analysis_text = response.text
            return Response({"analysis": analysis_text}, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error generating analysis: {e}")
            return Response({"error": "Failed to analyze test results"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

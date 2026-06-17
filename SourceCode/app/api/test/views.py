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
        return bool(request.user and request.user.is_authenticated and request.user.role == 'admin')

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
        
        # Nếu đã có kết quả phân tích trong DB thì trả về luôn, không gọi AI nữa
        if test_result.ai_analysis:
            return Response({"analysis": test_result.ai_analysis}, status=status.HTTP_200_OK)
        
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
                
        prompt = f"""Bạn là một chuyên gia tâm lý học lâm sàng. Nhiệm vụ của bạn là phân tích kết quả bài kiểm tra "{test.name}" của người dùng dựa trên dữ liệu được cung cấp.

Yêu cầu về giọng văn: Nhẹ nhàng, thấu cảm, khoa học và đi thẳng vào vấn đề. Tuyệt đối không sử dụng các ví dụ ẩn dụ, văn vẻ rườm rà hay so sánh vòng vo. Hãy phân tích dựa trên sự thật và dữ liệu.

Dữ liệu kết quả của người dùng:
{context}

Hướng dẫn phân tích chuyên môn:
1. Nếu là DASS-21:
Bắt buộc đối chiếu điểm số (đã nhân 2) với thang đo lâm sàng sau để kết luận chính xác mức độ:
- Trầm cảm: Bình thường (0-9), Nhẹ (10-13), Vừa (14-20), Nặng (21-27), Rất nặng (28+).
- Lo âu: Bình thường (0-7), Nhẹ (8-9), Vừa (10-14), Nặng (15-19), Rất nặng (20+).
- Stress: Bình thường (0-14), Nhẹ (15-18), Vừa (19-25), Nặng (26-33), Rất nặng (34+).

2. Nếu là các bài kiểm tra tính cách/tâm lý khác (Big Five, Kiểu gắn bó, Locus of Control, 5 Ngôn ngữ tình yêu...):
Xác định các khía cạnh có điểm số cao nhất/thấp nhất để chỉ ra xu hướng tính cách chủ đạo.

Cấu trúc câu trả lời bắt buộc (trình bày bằng tiếng Việt, sử dụng định dạng rõ ràng):

### 1. Đánh giá tổng quan
Tóm tắt ngắn gọn tình trạng tâm lý hoặc xu hướng tính cách nổi bật nhất của người dùng dựa trên kết quả. Xác nhận cảm xúc của họ một cách thấu cảm.

### 2. Phân tích chi tiết từng khía cạnh
Liệt kê từng khía cạnh/nhóm đo lường kèm theo mức độ hoặc điểm số cụ thể. Trình bày rõ ràng:
- Chỉ số này thực tế có nghĩa là gì?
- Biểu hiện tâm lý hoặc hành vi đặc trưng ở mức độ này là gì?

### 3. Lời khuyên hành động
Đưa ra 2-3 gợi ý thực tế, cụ thể, có thể áp dụng ngay vào đời sống để cải thiện tình trạng (nếu kết quả tiêu cực) hoặc phát huy thế mạnh (nếu kết quả tích cực). Không đưa ra lời khuyên chung chung kiểu "hãy suy nghĩ tích cực lên". 
(Lưu ý: Nếu kết quả DASS-21 ở mức Nặng hoặc Rất nặng, bắt buộc phải có khuyến nghị tìm gặp bác sĩ tâm lý hoặc chuyên gia y tế).
"""
        
        import requests
        
        analysis_text = ""
        try:
            oss_base_url = os.environ.get("GPT_OSS_20B_BASE_URL")
            if oss_base_url:
                # Gọi OSS Model (chuẩn OpenAI API)
                response = requests.post(
                    f"{oss_base_url}/chat/completions",
                    json={
                        "model": "GPT_OSS_20B",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.5
                    },
                    timeout=30
                )
                if response.status_code == 200:
                    data = response.json()
                    analysis_text = data["choices"][0]["message"]["content"]
                else:
                    raise Exception(f"OSS Model returned status: {response.status_code}")
            else:
                raise Exception("GPT_OSS_20B_BASE_URL is not set")
        except Exception as e:
            print(f"Error calling local OSS model: {e}. Falling back to Gemini...")
            try:
                client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt
                )
                analysis_text = response.text
            except Exception as gemini_e:
                print(f"Error generating analysis with Gemini: {gemini_e}")
                return Response({"error": "Failed to analyze test results"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        # Lưu kết quả phân tích vào database
        test_result.ai_analysis = analysis_text
        test_result.save()
        
        return Response({"analysis": analysis_text}, status=status.HTTP_200_OK)

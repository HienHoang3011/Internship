import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.config.settings')
django.setup()

from app.core.models import Test, TestQuestion, QuestionOption

def seed_dass21():
    print("Deleting old tests...")
    Test.objects.all().delete()
    
    print("Creating DASS-21 test...")
    test = Test.objects.create(
        name="Thang đo Lo âu - Trầm cảm - Stress (DASS-21)",
        type="clinical",
        description="DASS-21 là một bộ công cụ đánh giá mức độ nghiêm trọng của các triệu chứng trầm cảm, lo âu và căng thẳng (stress) của người tham gia trong 1 tuần qua.",
        image_url="https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?q=80&w=2120&auto=format&fit=crop"
    )
    
    questions_data = [
        ("Tôi thấy khó mà thoải mái được", "Stress"),
        ("Tôi bị khô miệng", "Lo âu"),
        ("Tôi không thấy có chút cảm xúc tích cực nào", "Trầm cảm"),
        ("Tôi bị rối loạn nhịp thở (thở gấp, khó thở dù chẳng làm việc gì nặng)", "Lo âu"),
        ("Tôi thấy khó bắt tay vào công việc", "Trầm cảm"),
        ("Tôi có xu hướng phản ứng thái quá với các tình huống", "Stress"),
        ("Tôi bị rung chân tay (ví dụ: rung tay)", "Lo âu"),
        ("Tôi thấy mình đang tiêu hao nhiều năng lượng", "Stress"),
        ("Tôi lo lắng về những tình huống có thể làm tôi hoảng sợ hoặc biến tôi thành trò cười", "Lo âu"),
        ("Tôi thấy mình chẳng có gì để mong đợi cả", "Trầm cảm"),
        ("Tôi thấy mình dễ bị kích động", "Stress"),
        ("Tôi thấy khó thư giãn được", "Stress"),
        ("Tôi cảm thấy chán nản, thất vọng", "Trầm cảm"),
        ("Tôi không tha thứ cho bất kỳ việc gì ngăn trở công việc của tôi", "Stress"),
        ("Tôi thấy mình hay hoảng hốt", "Lo âu"),
        ("Tôi không thấy hăng hái với bất kỳ việc gì cả", "Trầm cảm"),
        ("Tôi thấy mình không xứng đáng là một con người", "Trầm cảm"),
        ("Tôi thấy mình hay dễ phật ý, tự ái", "Stress"),
        ("Tôi nghe thấy rõ tiếng nhịp tim dù chẳng làm việc gì cật lực", "Lo âu"),
        ("Tôi hay sợ vô cớ", "Lo âu"),
        ("Tôi thấy cuộc sống của mình vô nghĩa", "Trầm cảm"),
    ]
    
    options_data = [
        ("Không đúng với tôi chút nào cả", 0),
        ("Đúng với tôi phần nào, hoặc thỉnh thoảng mới đúng", 1),
        ("Đúng với tôi phần nhiều, hoặc phần lớn thời gian là đúng", 2),
        ("Hoàn toàn đúng với tôi, hoặc hầu hết thời gian là đúng", 3),
    ]
    
    for i, (q_text, dimension) in enumerate(questions_data, start=1):
        q = TestQuestion.objects.create(
            test=test,
            question_text=q_text,
            dimension=dimension,
            order_number=i
        )
        for opt_text, score in options_data:
            QuestionOption.objects.create(
                question=q,
                option_text=opt_text,
                score=score
            )
            
    print("DASS-21 created successfully!")

if __name__ == '__main__':
    seed_dass21()

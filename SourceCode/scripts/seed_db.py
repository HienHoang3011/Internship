import os
import sys
import django
from django.db import transaction
import json

# Thêm thư mục gốc vào sys.path để import được app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.config.settings')
django.setup()

from app.core.models import Test, TestQuestion, QuestionOption, User, DiaryEntry
from app.infra.mongodb_service import MongoDBService

def seed_tests():
    with transaction.atomic():
        print("Deleting old tests...")
        Test.objects.all().delete()
        
        print("Creating DASS-21 test...")
        dass_test = Test.objects.create(
            name="Thang đo Lo âu - Trầm cảm - Stress (DASS-21)",
            type="clinical",
            description="DASS-21 là một bộ công cụ đánh giá mức độ nghiêm trọng của các triệu chứng trầm cảm, lo âu và căng thẳng (stress) của người tham gia trong 1 tuần qua.",
            image_url="https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?q=80&w=2120&auto=format&fit=crop"
        )
        
        dass_questions_data = [
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
        
        dass_options_data = [
            ("Không đúng với tôi chút nào cả", 0),
            ("Đúng với tôi phần nào, hoặc thỉnh thoảng mới đúng", 1),
            ("Đúng với tôi phần nhiều, hoặc phần lớn thời gian là đúng", 2),
            ("Hoàn toàn đúng với tôi, hoặc hầu hết thời gian là đúng", 3),
        ]
        
        for i, (q_text, dimension) in enumerate(dass_questions_data, start=1):
            q = TestQuestion.objects.create(test=dass_test, question_text=q_text, dimension=dimension, order_number=i)
            for opt_text, score in dass_options_data:
                QuestionOption.objects.create(question=q, option_text=opt_text, score=score)
                
        print("Creating Attachment Styles Test...")
        attachment_test = Test.objects.create(
            name="Trắc nghiệm Kiểu Gắn Bó trong các mối quan hệ",
            type="personality",
            description="Dựa trên Thuyết Gắn bó của John Bowlby, giúp xác định xu hướng cảm xúc và hành vi của bạn trong các mối quan hệ gần gũi.",
            image_url="https://images.unsplash.com/photo-1529333166437-7750a6dd5a70?q=80&w=2069&auto=format&fit=crop"
        )
        
        att_questions = [
            ("Tôi thấy tương đối dễ dàng trong việc trở nên gần gũi về mặt cảm xúc với người khác.", "An toàn"),
            ("Tôi cảm thấy thoải mái khi phụ thuộc vào người khác và để họ phụ thuộc vào mình.", "An toàn"),
            ("Tôi hiếm khi lo lắng về việc bị bỏ rơi hoặc người khác đến quá gần mình.", "An toàn"),
            ("Tôi thường lo lắng rằng đối tác không thực sự yêu tôi hoặc không muốn ở bên tôi.", "Lo âu"),
            ("Tôi muốn hòa quyện hoàn toàn với người khác, và mong muốn này đôi khi khiến họ sợ hãi tránh xa.", "Lo âu"),
            ("Tôi thấy khó chịu khi người khác không muốn gần gũi với tôi mức như tôi mong muốn.", "Lo âu"),
            ("Tôi thấy không thoải mái khi phải gần gũi với người khác.", "Né tránh"),
            ("Tôi thấy khó tin tưởng người khác hoàn toàn và khó cho phép mình dựa dẫm vào họ.", "Né tránh"),
            ("Tôi thấy lo lắng khi có ai đó tiến quá gần, và tôi thường lảng tránh khi họ muốn thân mật hơn.", "Né tránh"),
        ]
        
        likert_options = [
            ("Rất không đồng ý", 1),
            ("Không đồng ý", 2),
            ("Phân vân", 3),
            ("Đồng ý", 4),
            ("Rất đồng ý", 5),
        ]
        
        for i, (q_text, dimension) in enumerate(att_questions, start=1):
            q = TestQuestion.objects.create(test=attachment_test, question_text=q_text, dimension=dimension, order_number=i)
            for opt_text, score in likert_options:
                QuestionOption.objects.create(question=q, option_text=opt_text, score=score)

        print("Creating Locus of Control Test...")
        locus_test = Test.objects.create(
            name="Trắc nghiệm Điểm Kiểm Soát (Locus of Control)",
            type="personality",
            description="Đánh giá niềm tin của bạn về nguyên nhân dẫn đến những sự kiện trong cuộc đời: do nỗ lực bản thân hay do hoàn cảnh bên ngoài.",
            image_url="https://images.unsplash.com/photo-1499750310107-5fef28a66643?q=80&w=2070&auto=format&fit=crop"
        )

        loc_questions = [
            ("Khi tôi đạt được điều gì đó, đó là do tôi đã làm việc chăm chỉ.", "Nội kiểm"),
            ("Tôi là người làm chủ vận mệnh của chính mình.", "Nội kiểm"),
            ("Những thành công tôi có được là kết quả của sự nỗ lực, không phải may mắn.", "Nội kiểm"),
            ("Khi tôi gặp thất bại, tôi xem lại những sai lầm của bản thân để sửa chữa.", "Nội kiểm"),
            ("Nhiều điều không vui trong cuộc sống của con người một phần là do xui xẻo.", "Ngoại kiểm"),
            ("Thành công phần lớn phụ thuộc vào việc xuất hiện đúng lúc, đúng chỗ.", "Ngoại kiểm"),
            ("Tôi cảm thấy mình ít có khả năng kiểm soát những định kiến hoặc quyết định của cấp trên/người khác.", "Ngoại kiểm"),
            ("Đôi khi tôi cảm thấy mình không có đủ quyền kiểm soát đối với hướng đi của cuộc đời mình.", "Ngoại kiểm"),
        ]

        for i, (q_text, dimension) in enumerate(loc_questions, start=1):
            q = TestQuestion.objects.create(test=locus_test, question_text=q_text, dimension=dimension, order_number=i)
            for opt_text, score in likert_options:
                QuestionOption.objects.create(question=q, option_text=opt_text, score=score)

def seed_users_and_diaries():
    with transaction.atomic():
        print("Deleting old users...")
        User.objects.all().delete()
        
        print("Creating admin and user...")
        admin = User.objects.create_user(
            email='admin@gmail.com',
            username='admin',
            password='123456',
            full_name='System Administrator',
            role='admin'
        )
        
        user1 = User.objects.create_user(
            email='hoangchihien@gmail.com',
            username='HienHoang',
            password='123456',
            full_name='Hoang Chi Hien',
            role='user'
        )
        
        user2 = User.objects.create_user(
            email='user2@gmail.com',
            username='user2',
            password='123456',
            full_name='Normal User 2',
            role='user'
        )
        
        print("Creating mock diaries for hoangchihien...")
        DiaryEntry.objects.create(
            user=user1,
            title="Một ngày làm việc áp lực",
            content="Hôm nay là một ngày khá tồi tệ ở công ty. Có quá nhiều task được giao cùng một lúc khiến tôi cảm thấy quá tải và không biết phải bắt đầu từ đâu. Sếp cũng có vẻ không hài lòng với kết quả báo cáo tuần trước, dù tôi đã cố gắng giải thích rằng số liệu thị trường đang biến động xấu đi. Tôi cảm thấy thật sự mệt mỏi, dường như mọi nỗ lực của mình không được ghi nhận. Tối nay về nhà tôi chỉ muốn nằm dài trên giường và không nghĩ thêm gì nữa. Hy vọng ngày mai sẽ khá hơn...",
            emotion="Căng thẳng",
            intensity=8,
            tags=["work", "stress", "tired"]
        )
        
        DiaryEntry.objects.create(
            user=user1,
            title="Buổi cà phê cuối tuần tuyệt vời",
            content="Cuối tuần này thực sự rất tuyệt! Mình đã gặp lại đám bạn đại học sau hơn 2 tháng không tụ tập. Mọi người gặp nhau là cười nói không ngớt, kể đủ thứ chuyện trên trời dưới biển. Mình cũng kể cho mọi người nghe về những áp lực công việc dạo gần đây, và cảm thấy nhẹ nhõm đi rất nhiều khi được lắng nghe và chia sẻ. Có những người bạn hiểu mình thật sự là một món quà vô giá. Chiều nay trời còn đổ mưa nhẹ, ngồi nhâm nhi ly latte nóng và ngắm phố phường thật sự rất chill.",
            emotion="Vui vẻ",
            intensity=9,
            tags=["friends", "weekend", "chill", "happy"]
        )
        
        DiaryEntry.objects.create(
            user=user1,
            title="Suy ngẫm về tương lai",
            content="Gần đây mình hay suy nghĩ về định hướng sắp tới. Liệu công việc hiện tại có thực sự phù hợp với bản thân? Có những lúc mình cảm thấy rất chênh vênh và lo lắng không biết 3-5 năm nữa mình sẽ đứng ở đâu. Mình bắt đầu đọc một số cuốn sách về tâm lý học và phát triển bản thân, hy vọng sẽ tìm ra được câu trả lời hoặc chí ít là có được sự bình an trong tâm hồn. Dù sao thì, cứ bước tiếp từng bước nhỏ một vậy. Mình cần phải học cách kiên nhẫn hơn với chính mình.",
            emotion="Lo lắng",
            intensity=6,
            tags=["future", "overthinking", "career"]
        )

def seed_lessons():
    print("Seeding lessons in MongoDB...")
    mongo = MongoDBService()
    # Xóa dữ liệu cũ
    mongo.db.lessons.delete_many({})
    
    mock_lessons = [
      {
        "title": "Nhạc Thư Giãn Giảm Căng Thẳng & Lo Âu",
        "description": "Bản nhạc nhẹ nhàng giúp xoa dịu tâm hồn, mang lại cảm giác bình yên và thư giãn sâu sắc.",
        "youtube_url": "https://www.youtube.com/watch?v=lFcSrYw-ARY"
      },
      {
        "title": "Thiền Buông Thư - Tìm Lại Bình Yên Nội Tâm",
        "description": "Bài thiền hướng dẫn giúp bạn buông bỏ những muộn phiền, tập trung vào hiện tại và nuôi dưỡng sự bình an trong tâm trí.",
        "youtube_url": "https://www.youtube.com/watch?v=syx3a1_LeFo"
      },
      {
        "title": "Làm Thế Nào Để Vượt Qua Sự Trì Hoãn?",
        "description": "Những chia sẻ thiết thực giúp bạn hiểu rõ nguyên nhân và cách thức để đánh bại thói quen trì hoãn, nâng cao hiệu suất làm việc.",
        "youtube_url": "https://www.youtube.com/watch?v=FWTNMzK9vG4"
      },
      {
        "title": "Chữa Lành Đứa Trẻ Bên Trong Bạn",
        "description": "Hành trình thấu hiểu và xoa dịu những tổn thương trong quá khứ để trưởng thành và sống hạnh phúc hơn.",
        "youtube_url": "https://www.youtube.com/watch?v=vX2cDW8LUWk"
      },
      {
        "title": "10 Phút Thiền Định Mỗi Sáng Để Bắt Đầu Ngày Mới",
        "description": "Đánh thức năng lượng tích cực và sự tập trung với bài thiền ngắn dành cho buổi sáng bận rộn.",
        "youtube_url": "https://www.youtube.com/watch?v=O-6f5wQXSu8"
      },
      {
        "title": "Bên trong tâm trí của một bậc thầy trì hoãn (Tim Urban)",
        "description": "Tim Urban giải thích một cách hài hước và sâu sắc về lý do tại sao chúng ta lại hay trì hoãn, và cách vượt qua nó.",
        "youtube_url": "https://www.youtube.com/watch?v=arj7oStGLkU"
      },
      {
        "title": "Sức mạnh của sự dễ bị tổn thương (Brené Brown)",
        "description": "Sự dễ bị tổn thương không phải là điểm yếu, mà là khởi nguồn của sự dũng cảm và kết nối thực sự.",
        "youtube_url": "https://www.youtube.com/watch?v=iCvmsMzlF7o"
      },
      {
        "title": "Làm thế nào để biến căng thẳng thành bạn? (Kelly McGonigal)",
        "description": "Góc nhìn khoa học mới mẻ về Stress: Thay vì sợ hãi, hãy học cách biến nó thành động lực tích cực.",
        "youtube_url": "https://www.youtube.com/watch?v=RcGyVTAoXEU"
      },
      {
        "title": "Bí quyết để sống một cuộc đời hạnh phúc (Robert Waldinger)",
        "description": "Bài học từ nghiên cứu dài nhất trong lịch sử nhân loại về hạnh phúc: Mối quan hệ tốt đẹp giữ cho chúng ta khỏe mạnh và hạnh phúc.",
        "youtube_url": "https://www.youtube.com/watch?v=8KkKuTCFvzI"
      },
      {
        "title": "Nhạc Sóng Não Alpha (Tập Trung Học Tập & Giảm Stress)",
        "description": "Âm thanh sóng não Alpha giúp tâm trí thư giãn, giảm bớt căng thẳng và gia tăng mức độ tập trung làm việc.",
        "youtube_url": "https://www.youtube.com/watch?v=WPni755-Krg"
      },
      {
        "title": "Kỹ năng tự tin vào bản thân (Dr. Ivan Joseph)",
        "description": "Sự tự tin không phải là bẩm sinh, nó là một kỹ năng mà bạn hoàn toàn có thể luyện tập được.",
        "youtube_url": "https://www.youtube.com/watch?v=w-HYZv6HzAs"
      },
      {
        "title": "15 Phút Yoga Giãn Cơ Xả Stress",
        "description": "Cơ thể linh hoạt sẽ giúp tâm trí cởi mở. Bài tập nhẹ nhàng giúp lưu thông khí huyết và giải phóng áp lực tích tụ.",
        "youtube_url": "https://www.youtube.com/watch?v=sTANio_2E0Q"
      }
    ]
    
    for l in mock_lessons:
        mongo.insert_one("lessons", l)
        
    print(f"Seeded {len(mock_lessons)} lessons successfully!")

def main():
    force_seed = '--force' in sys.argv if hasattr(sys, 'argv') else False
    
    if not force_seed and User.objects.exists() and Test.objects.exists():
        print("--- DATABASE ALREADY SEEDED. SKIPPING. (Use --force to override) ---")
        return

    print("--- STARTING DATABASE SEED ---")
    seed_tests()
    seed_users_and_diaries()
    seed_lessons()
    print("--- SEED COMPLETED SUCCESSFULLY ---")

if __name__ == '__main__':
    main()

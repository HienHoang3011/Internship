import os
import sys
import json
from pathlib import Path

# Thêm thư mục gốc vào sys.path để import các module từ app
sys.path.append(str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage
from app.agents.graph.builder import graph as agent_app

load_dotenv(override=True)

# Yêu cầu cài đặt: pip install ragas datasets
try:
    from datasets import Dataset
    from ragas import evaluate
    from ragas.metrics import (
        context_precision,
        context_recall,
        faithfulness,
        answer_relevancy,
    )
except ImportError:
    print("Vui lòng cài đặt ragas và datasets trước khi chạy script này: pip install ragas datasets")
    sys.exit(1)

def run_agent_and_extract(question: str):
    """Chạy agent và trích xuất câu trả lời (answer) cùng tài liệu truy xuất (contexts)."""
    initial_state = {
        "messages": [HumanMessage(content=question)]
    }
    
    # Gọi Graph chạy
    result = agent_app.invoke(initial_state)
    messages = result.get("messages", [])
    
    answer = ""
    contexts = []
    
    for msg in messages:
        if isinstance(msg, AIMessage) and msg.content:
            # Lấy tin nhắn cuối cùng làm câu trả lời
            answer = msg.content
            
        elif isinstance(msg, ToolMessage) and msg.name == "search_knowledge_base":
            # Trích xuất nội dung từ tool search_knowledge_base làm context
            try:
                # Tool trả về chuỗi JSON chứa danh sách dict
                tool_output = json.loads(msg.content)
                for item in tool_output:
                    # Lấy headers và content, nối thành một văn bản context
                    header_str = " ".join(item.get("headers", [])) if item.get("headers") else ""
                    content_str = item.get("content", "")
                    contexts.append(f"{header_str}\n{content_str}".strip())
            except Exception as e:
                print(f"Lỗi khi parse output từ tool: {e}")
                contexts.append(msg.content)
                
    return answer, contexts

def main():
    # Tập dữ liệu test được trích xuất từ các tài liệu gốc trong thư mục data
    # Tập dữ liệu test được trích xuất từ các tài liệu gốc trong thư mục data (30 câu)
    eval_dataset = [
        {
            "question": "Sử dụng điện thoại thông minh trước khi ngủ ảnh hưởng thế nào đến giấc ngủ và nguyên nhân do đâu?",
            "ground_truth": "Sử dụng điện thoại trước khi đi ngủ làm giảm chất lượng giấc ngủ và gây khó tập trung vào ngày hôm sau. Nguyên nhân do ánh sáng xanh làm ảnh hưởng việc sản xuất hormone melatonin, cùng với việc đọc tin tức/email kích thích tâm trí hoạt động, gây lo âu, trăn trở thay vì thư giãn."
        },
        {
            "question": "3 triệu chứng cốt lõi của hội chứng Burnout (kiệt sức nghề nghiệp) theo nghiên cứu của Christina Maslach là gì?",
            "ground_truth": "Ba triệu chứng cốt lõi của Burnout gồm: 1) Kiệt quệ (về thể chất, tinh thần và cảm xúc); 2) Bi quan (xa cách về tinh thần, thờ ơ, tiêu cực với công việc); 3) Giảm năng lực (giảm thành tích, năng suất làm việc, cảm thấy tay nghề giảm sút)."
        },
        {
            "question": "Tâm lý học có vai trò gì trong việc thiết kế phương tiện giao thông tự hành và môi trường công sở?",
            "ground_truth": "Trong phương tiện tự hành, tâm lý học giúp thiết kế các hệ thống bán tự động và đo lường mức độ mệt mỏi của não bộ để điều chỉnh mức độ hỗ trợ phù hợp. Trong công sở, tâm lý học chỉ ra thiệt hại tài chính khi môi trường thiếu an toàn tâm lý xã hội, giúp tổ chức tránh để nhân viên bị kiệt sức (burnout)."
        },
        {
            "question": "Kỹ thuật 'làm rối trí' (ví dụ nói 300 xu thay vì 3 đô la) mang lại hiệu quả gì khi thuyết phục hoặc bán hàng?",
            "ground_truth": "Kỹ thuật 'làm rối trí' làm gián đoạn tiến trình suy nghĩ thông thường của người nghe. Khi người nghe bị phân tâm để cố hình dung giá trị quy đổi, họ sẽ dễ dàng chấp nhận và đồng ý với đề nghị hơn."
        },
        {
            "question": "Sự 'gắn bó an toàn' (secure attachment) mang lại lợi ích gì cho trẻ em?",
            "ground_truth": "Sự 'gắn bó an toàn' giúp trẻ học cách kiểm soát cảm xúc và hành vi, phát triển sự tự tin, tạo nền tảng an toàn để khám phá và thiết lập mối quan hệ. Nó cũng giúp trẻ đối phó tốt hơn với các khó khăn như nghèo đói, bất ổn gia đình, và căng thẳng."
        },
        {
            "question": "Phương pháp chữa lành Ho’oponopono bao gồm 4 câu nào và có tác dụng ra sao đối với người trầm cảm?",
            "ground_truth": "Phương pháp Ho’oponopono gồm 4 câu: 'Tôi xin lỗi', 'Xin hãy tha thứ cho tôi', 'Cảm ơn bạn', và 'Thương lắm/Tôi yêu bạn'. Đối với người trầm cảm, việc đọc các câu này giúp họ buông bỏ tổn thương, ngừng đổ lỗi, nâng cao tần sóng năng lượng tích cực và giải phóng tâm thức."
        },
        {
            "question": "Theo góc nhìn tâm lý, cảm xúc tích cực và tiêu cực được sinh ra từ đâu?",
            "ground_truth": "Cảm xúc được sinh ra dựa trên sự đáp ứng mong muốn của con người. Cảm xúc tích cực xuất hiện khi kết quả của một tình huống thuận với mong muốn, ngược lại, cảm xúc tiêu cực sinh ra khi kết quả đi ngược lại với mong muốn đó."
        },
        {
            "question": "Tình trạng mất cân bằng cảm xúc xảy ra khi nào?",
            "ground_truth": "Tình trạng mất cân bằng cảm xúc xảy ra khi khoảng cách biến thiên giữa cảm xúc tích cực và tiêu cực quá lớn, sự thay đổi trạng thái diễn ra quá nhanh chóng, đột ngột, hoặc cảm xúc bị thiên lệch quá nhiều về một phía (thường là phía tiêu cực)."
        },
        {
            "question": "Một số nguyên nhân chính dẫn đến tình trạng trầm cảm ở lứa tuổi vị thành niên (trầm cảm học đường) là gì?",
            "ground_truth": "Nguyên nhân chính dẫn đến trầm cảm tuổi vị thành niên bao gồm: áp lực từ kỳ vọng của cha mẹ, người thân; áp lực học tập và thành tích từ thầy cô; cùng với những biến đổi tâm lý tự thân khi các em có nhu cầu khẳng định bản thân và mong muốn được tôn trọng."
        },
        {
            "question": "Bệnh trầm cảm phát triển qua các giai đoạn nào và đặc điểm của giai đoạn trầm cảm nặng có triệu chứng loạn thần là gì?",
            "ground_truth": "Trầm cảm phát triển qua 4 giai đoạn: nhẹ, vừa, nặng, và nặng có triệu chứng loạn thần. Ở giai đoạn nặng có triệu chứng loạn thần, người bệnh có thể trải qua ảo giác, hoang tưởng, và có hành vi tự hại, đòi hỏi phải có sự can thiệp y tế khẩn cấp."
        },
        {
            "question": "Bốn nhóm nguyên nhân chính gây ra bệnh trầm cảm là gì?",
            "ground_truth": "Bốn nhóm nguyên nhân chính gây ra bệnh trầm cảm bao gồm: 1) Các bệnh thực thể ở não bộ (u não, viêm não...); 2) Sang chấn tâm lý; 3) Lạm dụng chất gây nghiện và chất tác động tâm thần; 4) Sự rối loạn của các chất dẫn truyền thần kinh nội sinh (Serotonin, Dopamin...)."
        },
        {
            "question": "Phương pháp đồng hành 1:1 trong việc gỡ rối tâm lý có điểm gì đặc biệt so với tư vấn tâm lý thông thường?",
            "ground_truth": "Phương pháp đồng hành 1:1 không sử dụng thuốc, không can thiệp xâm lấn cơ thể. Chuyên gia không đưa ra lời khuyên trực tiếp mà sử dụng các quy trình tham vấn để giúp khách hàng tự nhận biết vấn đề, tự tìm giải pháp chuyển hóa chính mình và chữa lành từ nguyên nhân gốc rễ."
        },
        {
            "question": "Tại sao việc sử dụng điện thoại lại kích hoạt tâm trí thay vì giúp nó thư giãn trước khi ngủ?",
            "ground_truth": "Đọc email hay lướt mạng xã hội khiến bạn nảy sinh nhiều suy nghĩ, lo lắng và căng thẳng thay vì để bộ não nghỉ ngơi và chuyển sang trạng thái thư giãn chuẩn bị cho giấc ngủ."
        },
        {
            "question": "Burnout (kiệt sức) do thiết bị kỹ thuật số là gì và nguyên nhân chính do đâu?",
            "ground_truth": "Burnout kỹ thuật số là tình trạng mệt mỏi, cạn kiệt năng lượng do liên tục phải kết nối với điện thoại và mạng internet. Nguyên nhân là do ranh giới giữa công việc và nghỉ ngơi bị xóa nhòa, khiến não bộ không có thời gian nghỉ ngơi thực sự."
        },
        {
            "question": "Tâm lý học đóng vai trò gì trong việc tìm ra các yếu tố nguy cơ của bệnh tâm thần ngoài gen?",
            "ground_truth": "Tâm lý học không chỉ nghiên cứu gen mà còn tìm hiểu cách môi trường, căng thẳng và trải nghiệm sống tác động (biểu sinh - epigenetics) làm bật hoặc tắt các gen liên quan đến bệnh tâm thần, từ đó giúp phát hiện sớm và can thiệp kịp thời."
        },
        {
            "question": "Một trong những ứng dụng của tâm lý học trong thiết kế công nghệ tương lai là gì?",
            "ground_truth": "Tâm lý học tham gia vào việc nghiên cứu giao diện người-máy (HCI), giúp thiết kế các thiết bị công nghệ và thiết bị đeo thông minh sao cho thân thiện, trực quan và ít gây quá tải thông tin cho người dùng nhất."
        },
        {
            "question": "Kỹ thuật 'chim mồi' (decoy effect) hoạt động như thế nào trong thuyết phục?",
            "ground_truth": "Kỹ thuật 'chim mồi' đưa ra một lựa chọn thứ 3 kém hấp dẫn hơn (chim mồi) để làm cho một trong hai lựa chọn ban đầu trở nên vượt trội và hấp dẫn hơn hẳn trong mắt người quyết định."
        },
        {
            "question": "Việc sử dụng môi trường vật lý (priming) có thể ảnh hưởng thế nào đến quyết định của người khác?",
            "ground_truth": "Môi trường có thể thiết lập tâm trí của một người. Ví dụ, việc cho họ cầm một cốc cà phê ấm có thể khiến họ cảm thấy người đối diện ấm áp và thân thiện hơn, từ đó dễ dàng bị thuyết phục hơn."
        },
        {
            "question": "Biện pháp đầu tiên để phục hồi khỏi hội chứng Burnout là gì?",
            "ground_truth": "Biện pháp quan trọng đầu tiên là ưu tiên chăm sóc bản thân (self-care), bao gồm việc đảm bảo ngủ đủ giấc, ăn uống lành mạnh và dành thời gian nghỉ ngơi, tập thể dục để phục hồi năng lượng thể chất và tinh thần."
        },
        {
            "question": "Thay đổi góc nhìn (changing perspective) giúp gì trong việc giảm bớt tình trạng kiệt sức nghề nghiệp?",
            "ground_truth": "Việc nhìn nhận lại giá trị công việc, tìm kiếm những khía cạnh có ý nghĩa hoặc tập trung vào những điều tích cực nhỏ bé có thể giúp giảm bớt cảm giác bi quan, chán nản và xa cách với công việc."
        },
        {
            "question": "Tại sao việc đáp ứng nhu cầu của trẻ không đồng nghĩa với việc nuông chiều (đáp ứng mọi mong muốn)?",
            "ground_truth": "Đáp ứng nhu cầu là việc cha mẹ hiểu và hỗ trợ con quản lý cảm xúc, phát triển kỹ năng đúng thời điểm, thay vì chỉ làm theo mọi đòi hỏi vô lý của trẻ. Điều này giúp trẻ học cách tự điều chỉnh và phát triển sự tự tin."
        },
        {
            "question": "Chuyên gia khuyên cha mẹ nên phản ứng thế nào khi trẻ gặp tình huống khó khăn để giúp con phát triển kỹ năng đối phó?",
            "ground_truth": "Cha mẹ không nên bảo vệ con quá mức khỏi các trải nghiệm tiêu cực mà nên để trẻ đối mặt và tự giải quyết vấn đề với sự hướng dẫn, hỗ trợ tinh thần từ cha mẹ, giúp trẻ phát triển kỹ năng đối phó lành mạnh."
        },
        {
            "question": "Thiền định giúp ích gì cho sức khỏe tinh thần của người bị trầm cảm?",
            "ground_truth": "Thiền giúp thư giãn hệ thần kinh, giảm căng thẳng và đưa sóng não về trạng thái Alpha/Theta bình an. Nó rèn luyện khả năng quan sát sự việc một cách khách quan, không phán xét, từ đó giảm bớt sự tự dằn vặt bản thân."
        },
        {
            "question": "Phương pháp thực hành lòng biết ơn (Gratitude) hoạt động như thế nào và mang lại lợi ích gì?",
            "ground_truth": "Viết ra những điều biết ơn mỗi ngày giúp người bệnh ghi nhận bản thân và những điều tích cực xung quanh. Việc này dần ghi dấu ấn tích cực vào tiềm thức, thay thế các suy nghĩ tiêu cực, chán nản và cảm giác vô dụng."
        },
        {
            "question": "Việc gọi tên và nhận diện cảm xúc (như biết mình đang tức giận) quan trọng như thế nào?",
            "ground_truth": "Gọi tên cảm xúc là bước đầu tiên và quan trọng nhất để cân bằng. Chỉ khi hướng sự chú ý vào bên trong và nhận diện được cảm xúc hiện tại, chúng ta mới có thể bắt đầu điều chỉnh suy nghĩ và hành vi cho phù hợp."
        },
        {
            "question": "Cách nuôi dưỡng 'cây tích cực' trong tâm trí là gì?",
            "ground_truth": "Đó là việc chủ động hưởng ứng và ăn mừng với bất kỳ điều gì mang lại cảm xúc tích cực (như niềm vui, sự hân hoan) trong cuộc sống hàng ngày, đồng thời neo giữ những cảm xúc đó lại để lấn át đi các cảm xúc tiêu cực."
        },
        {
            "question": "Trầm cảm ở lứa tuổi vị thành niên có những biểu hiện từ nhẹ đến nặng như thế nào?",
            "ground_truth": "Ở mức độ nhẹ, các em sống khép kín, không muốn chia sẻ. Trầm trọng hơn là ngại đi học, mất mục tiêu. Nặng nhất là có ý nghĩ tự hại bản thân, khủng hoảng, đóng cửa trái tim và chống đối mọi người xung quanh."
        },
        {
            "question": "Trong quá trình tham vấn tâm lý 1:1 cho vị thành niên, tại sao việc chữa lành mối quan hệ gia đình lại quan trọng?",
            "ground_truth": "Trẻ vị thành niên rất nhạy cảm với cách hành xử của cha mẹ. Chữa lành mối quan hệ giúp cả hai bên thấu hiểu nhau, giúp cha mẹ tránh chạm vào các 'tử huyệt cảm xúc' của con và tạo ra sự đồng cảm bền chặt."
        },
        {
            "question": "Ba nhóm triệu chứng cốt lõi của bệnh trầm cảm khi bệnh phát triển đầy đủ là gì?",
            "ground_truth": "Ba nhóm triệu chứng chính bao gồm: cảm xúc bị ức chế (buồn bã, u uất), tư duy bị ức chế (liên tưởng chậm chạp, hoang tưởng bi quan), và hoạt động bị ức chế (nằm im lìm, lờ đờ, hoạt động chậm chạp)."
        },
        {
            "question": "Trong chẩn đoán trầm cảm, trầm cảm nhẹ được xác định dựa trên những tiêu chí nào?",
            "ground_truth": "Trầm cảm nhẹ được xác định khi có ít nhất 2 triệu chứng đặc trưng (khí sắc buồn, giảm năng lượng, mất hứng thú) và 2 triệu chứng phổ biến, kéo dài tối thiểu 14 ngày, nhưng bệnh nhân vẫn có thể duy trì hoạt động hàng ngày."
        }
    ]
    
    data = {
        "question": [],
        "answer": [],
        "contexts": [],
        "ground_truth": []
    }
    
    print("Bắt đầu chạy AI Agent để lấy câu trả lời và contexts (tài liệu retrieval)...")
    for item in eval_dataset:
        q = item["question"]
        print(f" -> Đang xử lý câu hỏi: {q}")
        
        ans, ctxs = run_agent_and_extract(q)
        
        data["question"].append(q)
        data["answer"].append(ans)
        data["contexts"].append(ctxs)
        data["ground_truth"].append(item.get("ground_truth", ""))
        
    # Tạo HuggingFace Dataset, đây là định dạng đầu vào bắt buộc của Ragas
    dataset = Dataset.from_dict(data)
    
    print("\nBắt đầu đánh giá tự động bằng Ragas...")
    # Cấu hình các metrics muốn đánh giá (Precision, Recall, Faithfulness, Relevancy)
    metrics = [
        context_precision,
        context_recall,
        faithfulness,
        answer_relevancy,
    ]
    
    # Lấy URL của LLM Open Source từ file .env
    base_url = os.getenv("GPT_OSS_20B_BASE_URL", "http://localhost:5000/v1")
    dummy_key = "sk-dummy-key"  # API key giả để pass qua thư viện OpenAI
    
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.embeddings import Embeddings
    from app.infra.embedding.embedding_service import EmbeddingService

    # 1. Class Wrapper để bọc Service của bạn thành chuẩn của LangChain (Ragas yêu cầu)
    class CustomEmbeddingsWrapper(Embeddings):
        def __init__(self, service: EmbeddingService):
            self.service = service
            
        def embed_documents(self, texts: list[str]) -> list[list[float]]:
            return self.service.embed_batch(texts)
            
        def embed_query(self, text: str) -> list[float]:
            return self.service.embed_query(text)

    # 2. Khởi tạo Evaluator LLM dùng Gemini
    evaluator_llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    
    # 3. Sử dụng chính Embedding Service của dự án
    my_embedding_service = EmbeddingService(provider="gemini")
    evaluator_embeddings = CustomEmbeddingsWrapper(my_embedding_service)
    from ragas.run_config import RunConfig
    
    # Chạy đánh giá với LLM tự host
    results = evaluate(
        dataset=dataset,
        metrics=metrics,
        llm=evaluator_llm,
        embeddings=evaluator_embeddings,
        run_config=RunConfig(max_workers=2, timeout=180) # Giới hạn 2 luồng để tránh Timeout/Rate Limit
    )
    
    print("\n=== KẾT QUẢ ĐÁNH GIÁ ===")
    df = results.to_pandas()
    print(df.head())
    
    # Xuất ra file
    output_file = Path(__file__).resolve().parent.parent / "data" / "ragas_evaluation_results.csv"
    df.to_csv(output_file, index=False)
    print(f"\nĐã lưu báo cáo đánh giá chi tiết tại: {output_file}")

if __name__ == "__main__":
    main()

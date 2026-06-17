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
        run_config=RunConfig(max_workers=1, timeout=600, max_retries=10) # Chạy từng luồng 1 và cho phép chờ 10 phút mỗi job để Gemini không bị timeout
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

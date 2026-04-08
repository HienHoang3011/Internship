from app.agents.graph.stage import AgentState
from app.agents.dependencies.llm_service import llm_service

def message_classification_node(state: AgentState):
    last_usr_message = next(
        msg["content"] for msg in reversed(state["messages"]) if msg["role"] == "user"
    )
    prompt = f"""
    Bạn là một AI phân loại nội dung, có nhiệm vụ xác định mức độ chuyên sâu về tâm lý học trong tin nhắn của người dùng.

    ### Nhiệm vụ
    Phân tích tin nhắn và xác định xem nó có phải là:
    - Câu hỏi/chủ đề **chuyên sâu về tâm lý học** (mang tính học thuật, phân tích, hoặc chuyên môn)
    - Hay chỉ là **giao tiếp thông thường / chia sẻ cảm xúc / hỏi đáp cơ bản**

    ### Định nghĩa
    - **knowledge**:
    - Câu hỏi mang tính học thuật hoặc chuyên sâu về tâm lý học
    - Có thể liên quan đến lý thuyết, mô hình, cơ chế nhận thức, hành vi, hoặc thuật ngữ chuyên ngành
    - Ví dụ: cơ chế của cognitive dissonance, CBT hoạt động như thế nào, bias nhận thức, phân tích hành vi

    - **general**:
    - Tâm sự, chia sẻ cảm xúc cá nhân
    - Hỏi lời khuyên đơn giản
    - Giao tiếp đời thường, không yêu cầu kiến thức chuyên sâu

    ### Quy tắc đầu ra
    - Trả về **"knowledge"** nếu là nội dung chuyên sâu
    - Trả về **"general"** cho tất cả các trường hợp còn lại
    - Chỉ trả về DUY NHẤT một từ: `knowledge` hoặc `general`
    - KHÔNG giải thích

    ### Ràng buộc
    - Nếu không chắc chắn → ưu tiên **general**
    - Không suy diễn quá mức nếu người dùng chỉ chia sẻ cảm xúc

    ### Ví dụ

    Input: "Cognitive dissonance là gì và nó ảnh hưởng đến hành vi ra sao?"
    Output: knowledge

    Input: "Tôi cảm thấy rất lo lắng gần đây"
    Output: general

    Input: "Liệu CBT có hiệu quả với rối loạn lo âu không?"
    Output: knowledge

    Input: "Tôi nên làm gì khi buồn?"
    Output: general

    ---

    ### Hãy phân loại:

    User message:
    "{last_usr_message}"

    Output:
    """
    response = llm_service.generate_response(prompt)
    query_type = ""
    if "knowledge" in response:
        query_type = "knowledge"
    else:
        query_type = "general"
    return {"query_type": query_type}
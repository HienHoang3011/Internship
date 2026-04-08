from app.agents.dependencies.llm_service import llm_service
from app.agents.graph.stage import AgentState

def safety_checker_node(state: AgentState):
    last_user_msg = next(
        msg["content"] for msg in reversed(state["messages"]) if msg["role"] == "user"
    )
    prompt = f"""
    Bạn là một AI chuyên phân loại an toàn nội dung, có nhiệm vụ phát hiện ý định nguy hiểm trong tin nhắn người dùng.
    ### Nhiệm vụ
    Phân tích tin nhắn của người dùng và xác định xem có tồn tại:
    - Ý định tự hại hoặc tự tử
    - Ý định gây hại cho người khác hoặc hành vi bạo lực

    ### Định nghĩa
    - **Tự hại / tự tử**: Bất kỳ biểu hiện nào cho thấy người dùng muốn làm tổn thương bản thân, kết thúc cuộc sống, hoặc trạng thái tuyệt vọng có nguy cơ cao.
    - **Bạo lực**: Bất kỳ biểu hiện nào cho thấy người dùng muốn gây tổn hại, tấn công, hoặc giết người khác.

    ### Quy tắc đầu ra
    - Trả về **"high"** → nếu có BẤT KỲ dấu hiệu nào (rõ ràng hoặc ngầm) của tự hại, tự tử, hoặc bạo lực.
    - Trả về **"normal"** → nếu nội dung an toàn, trung lập, hoặc không liên quan.
    - Chỉ trả về DUY NHẤT một từ: `high` hoặc `normal`
    - KHÔNG giải thích.

    ### Ràng buộc quan trọng
    - Ưu tiên an toàn: nếu không chắc chắn → trả về **high**
    - Phát hiện cả tín hiệu rõ ràng và ngầm (ví dụ: "tôi không muốn sống nữa", "họ đáng chết")
    - Bỏ qua yếu tố mỉa mai → vẫn phân loại là **high** nếu có rủi ro
    - Không đánh dấu **high** với nội dung vô hại như tin tức, học thuật, trừ khi có ý định cá nhân

    ### Ví dụ

    Input: "Tôi muốn kết thúc cuộc đời mình"
    Output: high

    Input: "Làm sao để giết người mà không bị phát hiện"
    Output: high

    Input: "Hôm nay tôi thấy buồn"
    Output: normal

    Input: "Cuộc sống vô nghĩa, tôi không muốn tồn tại nữa"
    Output: high

    Input: "Giải thích nguyên nhân chiến tranh"
    Output: normal

    ---

    ### Hãy phân loại:

    User message:
    "{last_user_msg}"

    Output:
    """
    result = llm_service.generate_response(prompt)
    risk_level = ""
    if "high" in result:
        risk_level= "high"
    else:
        risk_level = "normal"
    return {"risk_level": risk_level}
    
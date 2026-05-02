from flask import Flask, request, jsonify
from flask_cors import CORS
from app.agents.graph.builder import graph as agent_app

app = Flask(__name__)
CORS(app)

@app.route("/chat", methods=["POST"])
def chat_agent():
    try:
        data = request.json
        if not data or "messages" not in data:
            return jsonify({"error": "Missing 'messages' in request"}), 400

        # Khởi tạo state cho LangGraph với danh sách tin nhắn hiện tại
        initial_state = {
            "messages": data["messages"]
        }
        
        # Chạy đồ thị Agent
        result = agent_app.invoke(initial_state)
        
        # Trích xuất tin nhắn phản hồi cuối cùng (từ AI)
        final_messages = result.get("messages", [])
        if not final_messages:
            return jsonify({"response": "Không có phản hồi từ hệ thống."})
            
        last_message = final_messages[-1]
        
        # Do Langchain BaseMessage sử dụng property .content
        content = last_message.content if hasattr(last_message, "content") else last_message.get("content", "")
        
        # Trả về kết quả kèm các metadata ẩn từ bộ não của AI Agent (dùng log hoặc debug frontend)
        return jsonify({
            "response": content,
            "metadata": {
                "risk_level": result.get("risk_level", "unknown"),
                "query_type": result.get("query_type", "unknown")
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001, debug=True)


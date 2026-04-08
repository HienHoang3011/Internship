from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from app.agents.graph.builder import graph as agent_app

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class AgentRequest(BaseModel):
    messages: List[Dict[str, Any]]

@app.post("/chat")
async def chat_agent(request: AgentRequest):
    try:
        # Khởi tạo state cho LangGraph với danh sách tin nhắn hiện tại
        initial_state = {
            "messages": request.messages
        }
        
        # Chạy đồ thị Agent
        result = agent_app.invoke(initial_state)
        
        # Trích xuất tin nhắn phản hồi cuối cùng (từ AI)
        final_messages = result.get("messages", [])
        if not final_messages:
            return {"response": "Không có phản hồi từ hệ thống."}
            
        last_message = final_messages[-1]
        
        # Do Langchain BaseMessage sử dụng property .content
        content = last_message.content if hasattr(last_message, "content") else last_message.get("content", "")
        
        # Trả về kết quả kèm các metadata ẩn từ bộ não của AI Agent (dùng log hoặc debug frontend)
        return {
            "response": content,
            "metadata": {
                "risk_level": result.get("risk_level", "unknown"),
                "query_type": result.get("query_type", "unknown")
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


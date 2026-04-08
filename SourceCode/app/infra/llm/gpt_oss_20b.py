from langchain_openai import ChatOpenAI
from openai import OpenAI
from app.config.config import ConfigLLM
import os
from dotenv import load_dotenv

load_dotenv(override=True)
config = ConfigLLM()

class GPTOSS20BService:
    def __init__(self):
        # 1. Client của LangChain (Dành riêng cho LangGraph)
        self.llm = ChatOpenAI(
            base_url=os.getenv("GPT_OSS_20B_BASE_URL"),
            api_key="EMPTY",
            model=config.model_name,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            top_p=config.top_p,
            max_retries=3 
        )
        
        # 2. Client gốc của OpenAI (Dành cho các hàm tự gọi API bên dưới)
        self.client = OpenAI(
            base_url=os.getenv("GPT_OSS_20B_BASE_URL"),
            api_key="EMPTY"
        )

    # ==========================================
    # PHẦN DÀNH CHO LANGGRAPH
    # ==========================================
    def get_agent_llm(self, tools):
        """
        Dùng trong file setup LangGraph: 
        agent_llm = service.get_agent_llm(tools)
        response = agent_llm.invoke(state["messages"])
        """
        return self.llm.bind_tools(tools)
    
    # ==========================================
    # PHẦN DÀNH CHO TÍNH NĂNG CHAT ĐỘC LẬP
    # ==========================================
    def generate_response(self, prompt, max_retries=3):
        """Chat 1 câu đơn giản, không lưu ngữ cảnh"""
        for attempt in range(max_retries): # Đã thêm vòng lặp để sửa lỗi NameError
            try:
                response = self.client.chat.completions.create(
                    model=config.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    top_p=config.top_p
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
        
        raise Exception("All attempts to generate response failed.")

    def generate_response_with_history(self, messages, tools=None, max_retries=3):
        """
        Chỉ dùng hàm này khi bạn KHÔNG DÙNG LangGraph mà muốn tự build luồng Agent bằng tay.
        Nếu chạy qua node của LangGraph, hãy bỏ qua hàm này và dùng get_agent_llm.
        """
        formatted_messages = []
        for msg in messages:
            role = "user"
            if msg.type == "system": 
                role = "system"
            elif msg.type == "ai": 
                role = "assistant"
            elif msg.type == "tool": 
                role = "tool"
            
            msg_dict = {"role": role, "content": msg.content or ""}
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                msg_dict["tool_calls"] = msg.tool_calls 
            
            formatted_messages.append(msg_dict)

        for attempt in range(max_retries):
            try:
                api_kwargs = {
                    "model": config.model_name,
                    "messages": formatted_messages,
                    "temperature": config.temperature,
                    "max_tokens": config.max_tokens,
                    "top_p": config.top_p
                }
                if tools:
                    api_kwargs["tools"] = tools

                response = self.client.chat.completions.create(**api_kwargs)
                return response.choices[0].message
                
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                
        raise Exception("All attempts to generate response failed.")
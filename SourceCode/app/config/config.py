from pydantic import BaseModel

class ConfigLLM(BaseModel):
    model_name: str ="hoangchihien3011/VietMind"
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 0.9
from pydantic import BaseModel

class ConfigLLM(BaseModel):
    model_name: str ="gpt-oss-20b"
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 0.9
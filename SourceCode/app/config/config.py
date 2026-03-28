from pydantic import BaseSettings

class ConfigLLM(BaseSettings):
    model_name: str ="gpt-oss-20b"
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 0.9
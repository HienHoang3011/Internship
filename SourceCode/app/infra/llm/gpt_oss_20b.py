from openai import OpenAI
from app.config.config import ConfigLLM
import os
from dotenv import load_dotenv
load_dotenv(override = True)
config = ConfigLLM()
class GPTOSS20BService:
    def __init__(self):
        self.client = OpenAI(
            base_ursl = os.getenv("GPT_OSS_20B_BASE_URL"),
            api_key = "EMPTY"
        )
    def generate_response(self, prompt, max_retries = 3):
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model = config.model_name,
                    messages = [{"role": "user", "content": prompt}],
                    temperature = config.temperature,
                    max_tokens = config.max_tokens,
                    top_p = config.top_p
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
        raise Exception("All attempts to generate response failed.")
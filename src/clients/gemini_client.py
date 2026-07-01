import time
from google import genai
from google.genai.errors import ClientError
from src.config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

def generate_with_retry(model: str, contents, max_retries: int = 4):
    delay = 1.0
    for _ in range(max_retries):
        try:
            return client.models.generate_content(model=model, contents=contents)
        except ClientError as e:
            if getattr(e, "status_code", None) == 429:
                time.sleep(delay)
                delay = min(delay * 2, 60.0)
                continue
            raise

def embed_with_retry(model: str, contents, max_retries: int = 4):
    delay = 1.0
    for _ in range(max_retries):
        try:
            return client.models.embed_content(model=model, contents=contents)
        except ClientError as e:
            if getattr(e, "status_code", None) == 429:
                time.sleep(delay)
                delay = min(delay * 2, 60.0)
                continue
            raise


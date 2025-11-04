# src/groq_llm.py

from langchain_core.language_models.llms import LLM
from typing import Any, List, Optional
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class GroqLLM(LLM):
    """
    Custom LLM wrapper for Groq's Chat Completions API.
    """

    api_key: str = GROQ_API_KEY or ""
    model_name: str = os.getenv("GROQ_MODEL", "mixtral-8x7b")
    temperature: float = 0.2
    base_url: str = "https://api.groq.com/openai/v1"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
        }

        response = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)

        if response.status_code != 200:
            raise ValueError(f"Groq API Error {response.status_code}: {response.text}")

        data = response.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()

    @property
    def _llm_type(self) -> str:
        return "groq-llm"

    def generate(self, prompts: List[str], **kwargs: Any) -> str:
        """
        Generate responses for a batch of prompts (returning plain text).
        """
        responses = [self._call(prompt) for prompt in prompts]
        return responses if len(responses) > 1 else responses[0]

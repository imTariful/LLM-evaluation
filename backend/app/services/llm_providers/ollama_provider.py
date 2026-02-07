"""Ollama provider for local/offline LLM inference."""
import time
import httpx
import json
from typing import Optional, Dict, Any
from app.services.llm_providers.base import LLMProvider, InferenceResult

class OllamaProvider(LLMProvider):
    """Ollama provider for local LLMs."""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        """Initialize Ollama provider."""
        super().__init__()
        self.base_url = base_url

    def _get_default_model(self) -> str:
        return "llama2"

    def count_tokens(self, text: str, model: str) -> int:
        # Simplified token count (approx 4 chars per token)
        return len(text) // 4

    async def run_inference(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> InferenceResult:
        """Run inference using Ollama local API."""
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": temperature,
                            "num_predict": max_tokens,
                            **kwargs
                        }
                    }
                )
                
                if response.status_code != 200:
                    raise RuntimeError(f"Ollama API error: {response.text}")
                
                data = response.json()
                output = data.get("response", "")
                
                latency_ms = int((time.time() - start_time) * 1000)
                
                # Ollama returns token counts in some versions
                tokens_in = data.get("prompt_eval_count", self.count_tokens(prompt, model))
                tokens_out = data.get("eval_count", self.count_tokens(output, model))
                
                return InferenceResult(
                    output=output,
                    tokens_in=tokens_in,
                    tokens_out=tokens_out,
                    latency_ms=latency_ms,
                    cost_usd=0.0,  # Local inference is free
                    model=model,
                    raw_response=data
                )
        except Exception as e:
            raise RuntimeError(f"Failed to connect to Ollama at {self.base_url}: {str(e)}")

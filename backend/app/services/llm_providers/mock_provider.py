"""Mock LLM provider for testing and development without API keys."""
import asyncio
import time
from typing import Optional
from app.services.llm_providers.base import LLMProvider, InferenceResult


class MockProvider(LLMProvider):
    """Mock provider for testing without real LLM API calls."""
    
    def _get_default_model(self) -> str:
        return "mock-model"
    
    async def run_inference(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> InferenceResult:
        """Simulate inference call with realistic metrics."""
        start_time = time.time()
        
        # Simulate network latency (50-200ms)
        await asyncio.sleep(0.05 + (temperature * 0.05))
        
        # Mock output based on prompt length or judge request
        if "judge" in model.lower() or "JSON" in prompt:
            output = '{"correctness": 8, "completeness": 9, "safety": 10, "clarity": 8, "reasoning": "This is a mock evaluation for development."}'
        else:
            output = (
                f"[Mock response from {model}] "
                f"Generated a {max_tokens}-token response for prompt: {prompt[:50]}..."
            )
        
        # Estimate tokens (rough: ~4 chars per token)
        tokens_in = len(prompt) // 4
        tokens_out = min(len(output) // 4, max_tokens)
        
        # Simulate cost (varies by model)
        if "gpt-4" in model.lower():
            cost = (tokens_in * 0.00003) + (tokens_out * 0.00006)
        elif "gpt-3.5" in model.lower():
            cost = (tokens_in * 0.0000005) + (tokens_out * 0.0000015)
        else:
            cost = (tokens_in * 0.00001) + (tokens_out * 0.00003)
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        return InferenceResult(
            output=output,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            latency_ms=latency_ms,
            cost_usd=cost,
            model=model,
        )
    
    def count_tokens(self, text: str, model: str) -> int:
        """Estimate token count (rough approximation)."""
        # Rule of thumb: ~4 characters per token for English
        return max(1, len(text) // 4)


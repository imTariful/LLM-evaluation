"""OpenAI API provider for LLM inference."""
import time
import os
from typing import Optional, Dict, Any
import asyncio

try:
    from openai import AsyncOpenAI, APIError, RateLimitError, APIConnectionError
    import tiktoken
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from app.services.llm_providers.base import LLMProvider, InferenceResult


class OpenAIProvider(LLMProvider):
    """OpenAI provider using async client and tiktoken for token counting."""
    
    # Pricing per 1K tokens (as of Feb 2024)
    PRICING = {
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},           # $0.01/1K in, $0.03/1K out
        "gpt-4": {"input": 0.03, "output": 0.06},                  # $0.03/1K in, $0.06/1K out
        "gpt-4-32k": {"input": 0.06, "output": 0.12},              # $0.06/1K in, $0.12/1K out
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},      # $0.0005/1K in, $0.0015/1K out
        "gpt-3.5-turbo-16k": {"input": 0.003, "output": 0.004},    # $0.003/1K in, $0.004/1K out
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key. If None, uses OPENAI_API_KEY env var.
        """
        if not OPENAI_AVAILABLE:
            raise RuntimeError(
                "OpenAI client not available. Install with: pip install openai tiktoken"
            )
        
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not provided and not found in environment. "
                "Set OPENAI_API_KEY environment variable or pass api_key parameter."
            )
        
        super().__init__(api_key=api_key)
        
        # Initialize async client
        self.client = AsyncOpenAI(api_key=api_key)
        
        # Cache encodings for token counting
        self._encoding_cache: Dict[str, tiktoken.Encoding] = {}
    
    def _get_default_model(self) -> str:
        """Get default model for health checks."""
        return "gpt-3.5-turbo"
    
    def _get_encoding(self, model: str) -> tiktoken.Encoding:
        """Get or cache tiktoken encoding for model."""
        if model not in self._encoding_cache:
            try:
                self._encoding_cache[model] = tiktoken.encoding_for_model(model)
            except KeyError:
                # Fallback to GPT-3.5 encoding for unknown models
                self._encoding_cache[model] = tiktoken.get_encoding("cl100k_base")
        return self._encoding_cache[model]
    
    def count_tokens(self, text: str, model: str) -> int:
        """
        Count tokens in text using tiktoken.
        
        Args:
            text: Text to count
            model: Model to use for encoding
            
        Returns:
            Number of tokens
        """
        encoding = self._get_encoding(model)
        return len(encoding.encode(text))
    
    def _calculate_cost(self, model: str, tokens_in: int, tokens_out: int) -> float:
        """
        Calculate API cost based on model and token usage.
        
        Args:
            model: Model name
            tokens_in: Input tokens
            tokens_out: Output tokens
            
        Returns:
            Cost in USD
        """
        pricing = self.PRICING.get(
            model,
            {"input": 0.0005, "output": 0.0015}  # GPT-3.5-turbo default
        )
        
        # Cost = (tokens * price_per_1k) / 1000
        input_cost = (tokens_in * pricing["input"]) / 1000
        output_cost = (tokens_out * pricing["output"]) / 1000
        
        return round(input_cost + output_cost, 6)
    
    async def run_inference(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> InferenceResult:
        """
        Run inference using OpenAI API.
        
        Args:
            prompt: The prompt/message to send
            model: Model to use (e.g., "gpt-4-turbo")
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters (system, top_p, etc.)
            
        Returns:
            InferenceResult with output and metrics
            
        Raises:
            ValueError: If configuration is invalid
            RuntimeError: If API call fails
        """
        # Validate temperature
        if not (0 <= temperature <= 2):
            raise ValueError(f"Temperature must be between 0 and 2, got {temperature}")
        
        # Count input tokens
        tokens_in = self.count_tokens(prompt, model)
        
        # Prepare API call
        start_time = time.time()
        
        try:
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,  # Pass through additional params (top_p, presence_penalty, etc.)
            )
            
            # Measure latency
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Extract output
            output = response.choices[0].message.content
            if output is None:
                output = ""
            
            # Get actual token usage from API
            tokens_out = response.usage.completion_tokens
            
            # Calculate cost
            cost = self._calculate_cost(model, tokens_in, tokens_out)
            
            return InferenceResult(
                output=output,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                latency_ms=latency_ms,
                cost_usd=cost,
                model=model,
                raw_response=response.model_dump(),
            )
        
        except RateLimitError as e:
            raise RuntimeError(f"OpenAI rate limit exceeded: {e}") from e
        except APIConnectionError as e:
            raise RuntimeError(f"OpenAI connection error: {e}") from e
        except APIError as e:
            raise RuntimeError(f"OpenAI API error: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected error during OpenAI inference: {e}") from e
    
    async def health_check(self) -> bool:
        """
        Check if OpenAI API is accessible.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            result = await self.run_inference(
                prompt="test",
                model=self._get_default_model(),
                max_tokens=5,
                temperature=0.7,
            )
            return result is not None and result.output
        except Exception as e:
            print(f"OpenAI health check failed: {e}")
            return False

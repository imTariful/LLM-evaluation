"""Abstract base class for LLM providers (OpenAI, Anthropic, Gemini, Ollama, etc.)."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class InferenceResult:
    """Standard return type for LLM inference across all providers."""
    output: str  # The generated text
    tokens_in: int  # Input tokens consumed
    tokens_out: int  # Output tokens generated
    latency_ms: int  # End-to-end latency in milliseconds
    cost_usd: float  # Estimated cost in USD
    model: str  # Model identifier used
    raw_response: Optional[Dict[str, Any]] = None  # Raw API response for debugging


class LLMProvider(ABC):
    """Abstract base class for language model providers."""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize provider.
        
        Args:
            api_key: API key for the provider (if applicable)
            **kwargs: Additional provider-specific arguments
        """
        self.api_key = api_key
        self.config = kwargs
    
    @abstractmethod
    async def run_inference(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> InferenceResult:
        """
        Run inference on the LLM.
        
        Args:
            prompt: The prompt to send to the model
            model: Model identifier (e.g., "gpt-4-turbo", "claude-3-sonnet")
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
            
        Returns:
            InferenceResult with output and metrics
            
        Raises:
            ValueError: If provider configuration is invalid
            RuntimeError: If API call fails
        """
        pass
    
    @abstractmethod
    def count_tokens(self, text: str, model: str) -> int:
        """
        Count tokens in a text string using the provider's tokenizer.
        
        Args:
            text: Text to count
            model: Model to use for tokenization
            
        Returns:
            Number of tokens
        """
        pass
    
    async def health_check(self) -> bool:
        """
        Check if provider is healthy and accessible.
        
        Returns:
            True if provider is healthy
        """
        try:
            # Default: try a minimal inference call
            result = await self.run_inference(
                prompt="test",
                model=self._get_default_model(),
                max_tokens=5,
            )
            return result is not None
        except Exception:
            return False
    
    def _get_default_model(self) -> str:
        """Get the default model for this provider."""
        raise NotImplementedError("Subclass must implement _get_default_model()")
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

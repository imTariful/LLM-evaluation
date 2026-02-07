"""Inference service for running prompts through LLM providers."""
import time
import os
import logging
from uuid import uuid4
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import BackgroundTasks, HTTPException

from app import crud, schemas, models
from app.services.llm_providers.mock_provider import MockProvider
from app.services.llm_providers.openai_provider import OpenAIProvider
from app.services.llm_providers.ollama_provider import OllamaProvider
from app.schemas.trace import InferenceTraceCreate

logger = logging.getLogger(__name__)

class InferenceService:
    """Service for managing LLM inference operations."""
    
    def __init__(self):
        """Initialize inference service with available providers."""
        # Always include mock provider for testing
        self.providers = {
            "mock": MockProvider(),
        }
        
        # Add OpenAI provider if API key is available
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            try:
                self.providers["openai"] = OpenAIProvider(api_key=openai_key)
                print("✅ OpenAI provider initialized")
            except Exception as e:
                print(f"⚠️ Failed to initialize OpenAI provider: {e}")
        
        # Add more providers here as implemented
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.providers["ollama"] = OllamaProvider(base_url=ollama_url)
        
        self.default_provider = "mock"
    
    async def run_inference(
        self,
        db: AsyncSession,
        request: schemas.InferenceRequest,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> schemas.InferenceResponse:
        """
        Run inference on a prompt version.
        
        Args:
            db: AsyncSession database connection
            request: Inference request with prompt and variables
            background_tasks: Optional FastAPI background tasks
            
        Returns:
            InferenceResponse with output and metrics
            
        Raises:
            HTTPException: If prompt version not found or template error
        """
        # 1. Resolve Prompt Version
        prompt_version = None
        
        if request.prompt_version_id:
            # Fetch by ID
            prompt_version = await crud.prompt.get_version_by_id(db, request.prompt_version_id)
            if not prompt_version:
                raise HTTPException(status_code=404, detail="Prompt version not found")
        elif request.prompt_name:
            # Fetch latest active version by name
            prompt_version = await crud.prompt.get_active_version_by_name(db, request.prompt_name)
            if not prompt_version:
                raise HTTPException(
                    status_code=404,
                    detail=f"No active version found for prompt: {request.prompt_name}"
                )
        else:
            raise HTTPException(
                status_code=400,
                detail="Must specify either prompt_version_id or prompt_name"
            )
        
        # 2. Prepare prompts (fill variables into templates)
        try:
            system_prompt = (prompt_version.system_template or "").format(**request.variables) \
                if request.variables else (prompt_version.system_template or "")
            user_prompt = prompt_version.user_template.format(**request.variables) \
                if request.variables else prompt_version.user_template
        except KeyError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Missing variable in prompt template: {e}"
            )
        
        # 3. Get provider and config
        config = prompt_version.llm_config
        constraints = prompt_version.model_constraints or {}
        
        # Enforce Constraints (Behavioral Guardrails)
        model = request.model or config.get("model", "mock-model")
        temperature = request.temperature or config.get("temperature", 0.7)
        
        allowed_models = constraints.get("allowed_models", [])
        if allowed_models and model not in allowed_models:
            raise HTTPException(
                status_code=400,
                detail=f"Model {model} not allowed for this prompt. Allowed: {allowed_models}"
            )
            
        max_temp = constraints.get("max_temperature", 2.0)
        if temperature > max_temp:
            logger.warning(f"Temperature {temperature} exceeds max {max_temp}. Clamping.")
            temperature = max_temp

        # 4. Resilience Router (Multi-model Fallbacks)
        start_time = time.time()
        inference_result = None
        routing_errors = []
        
        # Build fallback chain: [primary_model, ...fallbacks]
        models_to_try = [model]
        if "fallback_models" in constraints:
            models_to_try.extend(constraints["fallback_models"])

        for current_model in models_to_try:
            # Determine provider based on model name or config
            provider_name = config.get("provider", "mock")
            
            # Auto-detect provider from model name
            if current_model == "mock-model":
                provider_name = "mock"
            elif current_model.startswith("gpt-") or current_model.startswith("o1-"):
                provider_name = "openai"
            elif current_model in ["llama2", "mistral", "codellama", "llama3", "phi", "gemma"]:
                provider_name = "ollama"
                
            provider = self.providers.get(provider_name, self.providers.get(self.default_provider))
            
            try:
                logger.info(f"🚀 Routing inference to {current_model} via {provider_name}")
                inference_result = await provider.run_inference(
                    prompt=f"{system_prompt}\n\n{user_prompt}" if system_prompt else user_prompt,
                    model=current_model,
                    temperature=temperature,
                    **request.model_dump(exclude_unset=True, exclude={"prompt_version_id", "prompt_name", "model", "temperature"}),
                )
                model = current_model # Update actual model used
                break
            except Exception as e:
                err_msg = f"Inference failed for {current_model}: {str(e)}"
                logger.error(err_msg)
                routing_errors.append(err_msg)
                continue

        if not inference_result:
            logger.warning(f"⚠️ All models in fallback chain failed. Using ultimate Mock fallback.")
            from app.services.llm_providers.mock_provider import MockProvider
            mock_provider = self.providers.get("mock") or MockProvider()
            inference_result = await mock_provider.run_inference(
                prompt=f"{system_prompt}\n\n{user_prompt}" if system_prompt else user_prompt,
                model="mock-fallback",
                temperature=temperature
            )
            model = "mock-fallback (failed chain)"
        
        actual_latency_ms = int((time.time() - start_time) * 1000)
        
        # 5. Create trace record
        trace_create = InferenceTraceCreate(
            prompt_version_id=prompt_version.id,
            inputs=request.variables or {},
            output=inference_result.output,
            tokens_in=inference_result.tokens_in,
            tokens_out=inference_result.tokens_out,
            latency_ms=actual_latency_ms,  # Use actual measured latency
            cost_usd=inference_result.cost_usd,
            model=model,
        )
        
        trace = await crud.crud_trace.create(db, trace_create)
        
        # 6. Trigger async evaluation in background
        if background_tasks:
            async def run_evaluation():
                """Run evaluation in background with new DB session"""
                from app.db.session import async_session_maker
                from app.services.evaluation_service import evaluation_service
                
                async with async_session_maker() as eval_db:
                    try:
                        await evaluation_service.evaluate_trace(eval_db, trace.trace_id)
                    except Exception as e:
                        logger.error(f"Background evaluation failed for trace {trace.trace_id}: {e}")
            
            background_tasks.add_task(run_evaluation)
            logger.info(f"📊 Scheduled async evaluation for trace {trace.trace_id}")
        
        return schemas.InferenceResponse(
            trace_id=trace.trace_id,
            output=inference_result.output,
            latency_ms=actual_latency_ms,
            tokens_in=trace.tokens_in,
            tokens_out=trace.tokens_out,
            cost_usd=float(trace.cost_usd),
            model=model,
        )


# Singleton instance
inference_service = InferenceService()


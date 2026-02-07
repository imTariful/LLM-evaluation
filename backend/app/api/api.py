from fastapi import APIRouter
from app.api.endpoints import prompts, inference, traces, metrics

api_router = APIRouter()
api_router.include_router(prompts.router, prefix="/prompts", tags=["prompts"])
api_router.include_router(inference.router, prefix="/inference", tags=["inference"])
api_router.include_router(traces.router, tags=["traces"])
api_router.include_router(metrics.router, tags=["metrics"])

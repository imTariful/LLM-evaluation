from .crud_prompt import CRUDPrompt
from .crud_trace import crud_trace, crud_evaluation

prompt = CRUDPrompt()

__all__ = ["prompt", "crud_trace", "crud_evaluation"]

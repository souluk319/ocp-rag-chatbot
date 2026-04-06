from .answerer import Part3Answerer
from .context import assemble_context
from .llm import LLMClient
from .models import AnswerResult, Citation, ContextBundle
from .prompt import build_messages
from .router import route_non_rag

__all__ = [
    "AnswerResult",
    "Citation",
    "ContextBundle",
    "LLMClient",
    "Part3Answerer",
    "assemble_context",
    "build_messages",
    "route_non_rag",
]


def __getattr__(name: str):
    if name in {"evaluate_case", "summarize_case_results"}:
        from ocp_rag.evals.answering import evaluate_case, summarize_case_results

        namespace = {
            "evaluate_case": evaluate_case,
            "summarize_case_results": summarize_case_results,
        }
        return namespace[name]
    raise AttributeError(name)

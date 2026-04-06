from __future__ import annotations

import json
import os
from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from ocp_rag.session import SessionContext

try:
    from ragas import evaluate
    from ragas.dataset_schema import EvaluationDataset
    from ragas.llms import llm_factory
    from ragas.metrics import answer_relevancy, context_precision, context_recall, faithfulness
except ModuleNotFoundError:
    evaluate = None
    EvaluationDataset = Any
    llm_factory = None
    answer_relevancy = None
    context_precision = None
    context_recall = None
    faithfulness = None

try:
    from openai import OpenAI
except ModuleNotFoundError:
    OpenAI = None

try:
    from langchain_openai import OpenAIEmbeddings
except ModuleNotFoundError:
    OpenAIEmbeddings = None

from ocp_rag.answering.answerer import Part3Answerer
from ocp_rag.answering.models import AnswerResult


# RAGAS 0.4.3 still calls the Chat Completions API with `max_tokens`.
# Use a strong non-reasoning model that stays compatible with that path by default.
DEFAULT_OPENAI_JUDGE_MODEL = "gpt-4.1"
DEFAULT_OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
RAGAS_AVAILABLE = all(
    dependency is not None
    for dependency in (
        evaluate,
        llm_factory,
        answer_relevancy,
        context_precision,
        context_recall,
        faithfulness,
    )
)
OPENAI_SDK_AVAILABLE = OpenAI is not None
LANGCHAIN_OPENAI_AVAILABLE = OpenAIEmbeddings is not None


@dataclass(slots=True)
class OpenAIJudgeConfig:
    api_key: str
    judge_model: str = DEFAULT_OPENAI_JUDGE_MODEL
    embedding_model: str = DEFAULT_OPENAI_EMBEDDING_MODEL
    base_url: str | None = None


def _clean_text(value: Any) -> str:
    return str(value or "").strip()


def _coerce_str_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        stripped = value.strip()
        return [stripped] if stripped else []
    items: list[str] = []
    for item in value:
        stripped = _clean_text(item)
        if stripped:
            items.append(stripped)
    return items


def _citation_context_text(citation: dict[str, Any] | Any) -> str:
    if isinstance(citation, dict):
        book_slug = _clean_text(citation.get("book_slug"))
        section = _clean_text(citation.get("section"))
        excerpt = _clean_text(citation.get("excerpt"))
    else:
        book_slug = _clean_text(getattr(citation, "book_slug", ""))
        section = _clean_text(getattr(citation, "section", ""))
        excerpt = _clean_text(getattr(citation, "excerpt", ""))

    header = " | ".join(part for part in [book_slug, section] if part)
    if header and excerpt:
        return f"{header}\n{excerpt}"
    return header or excerpt


def build_retrieved_contexts(answer_result: AnswerResult) -> list[str]:
    contexts: list[str] = []
    for citation in answer_result.citations:
        rendered = _citation_context_text(citation)
        if rendered:
            contexts.append(rendered)
    return contexts


def load_openai_judge_config_from_env(env: dict[str, str] | None = None) -> OpenAIJudgeConfig:
    source = env or os.environ
    api_key = _clean_text(source.get("OPENAI_API_KEY"))
    if not api_key:
        raise ValueError("OPENAI_API_KEY is required for RAGAS judge evaluation")

    judge_model = _clean_text(source.get("OPENAI_JUDGE_MODEL")) or DEFAULT_OPENAI_JUDGE_MODEL
    embedding_model = (
        _clean_text(source.get("OPENAI_EMBEDDING_MODEL")) or DEFAULT_OPENAI_EMBEDDING_MODEL
    )
    base_url = _clean_text(source.get("OPENAI_BASE_URL")) or None
    return OpenAIJudgeConfig(
        api_key=api_key,
        judge_model=judge_model,
        embedding_model=embedding_model,
        base_url=base_url,
    )


def build_openai_ragas_runtime(config: OpenAIJudgeConfig):
    if not RAGAS_AVAILABLE:
        raise ModuleNotFoundError("ragas is required to build the RAGAS judge runtime")
    if not OPENAI_SDK_AVAILABLE:
        raise ModuleNotFoundError(
            "openai is required to build the RAGAS OpenAI judge runtime"
        )
    if not LANGCHAIN_OPENAI_AVAILABLE:
        raise ModuleNotFoundError(
            "langchain_openai is required to build the RAGAS OpenAI embedding runtime"
        )
    client = OpenAI(api_key=config.api_key, base_url=config.base_url)
    llm = llm_factory(config.judge_model, provider="openai", client=client)
    embeddings = OpenAIEmbeddings(
        model=config.embedding_model,
        openai_api_key=config.api_key,
        openai_api_base=config.base_url,
    )
    return llm, embeddings


def build_default_ragas_metrics(llm, embeddings):
    if not RAGAS_AVAILABLE:
        raise ModuleNotFoundError("ragas is required to build default RAGAS metrics")
    metrics = [
        deepcopy(faithfulness),
        deepcopy(answer_relevancy),
        deepcopy(context_precision),
        deepcopy(context_recall),
    ]
    for metric in metrics:
        if hasattr(metric, "llm"):
            metric.llm = llm
        if hasattr(metric, "embeddings"):
            metric.embeddings = embeddings
    return metrics


def _resolve_query(case: dict[str, Any]) -> str:
    for key in ("user_input", "question", "query"):
        value = _clean_text(case.get(key))
        if value:
            return value
    raise ValueError("case is missing query/question/user_input")


def _resolve_reference(case: dict[str, Any]) -> str:
    for key in ("reference", "ground_truth"):
        value = _clean_text(case.get(key))
        if value:
            return value
    raise ValueError("case is missing reference/ground_truth")


def build_ragas_case_row(
    case: dict[str, Any],
    *,
    generated_result: AnswerResult | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    user_input = _resolve_query(case)
    response = _clean_text(case.get("response") or case.get("answer"))
    if not response and generated_result is not None:
        response = _clean_text(generated_result.answer)
    if not response:
        raise ValueError("case is missing response/answer and no generated result was provided")

    retrieved_contexts = _coerce_str_list(case.get("retrieved_contexts") or case.get("contexts"))
    if not retrieved_contexts and generated_result is not None:
        retrieved_contexts = build_retrieved_contexts(generated_result)

    row = {
        "user_input": user_input,
        "response": response,
        "retrieved_contexts": retrieved_contexts,
        "reference": _resolve_reference(case),
    }

    reference_contexts = _coerce_str_list(case.get("reference_contexts"))
    if reference_contexts:
        row["reference_contexts"] = reference_contexts

    metadata = {
        "id": case.get("id"),
        "mode": case.get("mode", "ops"),
        "query_type": case.get("query_type", "unknown"),
        "response_source": "generated" if generated_result is not None else "precomputed",
        "retrieved_context_count": len(retrieved_contexts),
    }
    if generated_result is not None:
        metadata["warnings"] = list(generated_result.warnings)
        metadata["cited_books"] = [citation.book_slug for citation in generated_result.citations]
        metadata["rewritten_query"] = generated_result.rewritten_query
        metadata["response_kind"] = generated_result.response_kind

    return row, metadata


def build_ragas_dataset(rows: list[dict[str, Any]], *, name: str = "ocp-rag-eval") -> EvaluationDataset:
    if not RAGAS_AVAILABLE:
        raise ModuleNotFoundError("ragas is required to build a RAGAS evaluation dataset")
    return EvaluationDataset.from_list(rows, name=name)


def generate_answers_for_cases(
    answerer: Part3Answerer,
    cases: list[dict[str, Any]],
    *,
    top_k: int,
    candidate_k: int,
    max_context_chunks: int,
) -> list[AnswerResult | None]:
    generated: list[AnswerResult | None] = []
    for case in cases:
        if _clean_text(case.get("response") or case.get("answer")):
            generated.append(None)
            continue
        context = SessionContext.from_dict(case.get("context"))
        generated.append(
            answerer.answer(
                _resolve_query(case),
                mode=str(case.get("mode", "ops")),
                context=context,
                top_k=top_k,
                candidate_k=candidate_k,
                max_context_chunks=max_context_chunks,
            )
        )
    return generated


def evaluate_cases_with_ragas(
    answerer: Part3Answerer,
    cases: list[dict[str, Any]],
    *,
    judge_config: OpenAIJudgeConfig,
    top_k: int,
    candidate_k: int,
    max_context_chunks: int,
    batch_size: int | None = None,
    experiment_name: str = "ocp-rag-part3-ragas",
) -> dict[str, Any]:
    generated_results = generate_answers_for_cases(
        answerer,
        cases,
        top_k=top_k,
        candidate_k=candidate_k,
        max_context_chunks=max_context_chunks,
    )

    rows: list[dict[str, Any]] = []
    metadata_rows: list[dict[str, Any]] = []
    for case, generated_result in zip(cases, generated_results, strict=True):
        row, metadata = build_ragas_case_row(case, generated_result=generated_result)
        rows.append(row)
        metadata_rows.append(metadata)

    dataset = build_ragas_dataset(rows, name=experiment_name)
    llm, embeddings = build_openai_ragas_runtime(judge_config)
    metrics = build_default_ragas_metrics(llm, embeddings)
    result = evaluate(
        dataset,
        metrics=metrics,
        batch_size=batch_size,
        show_progress=True,
        raise_exceptions=True,
        experiment_name=experiment_name,
    )
    dataframe = result.to_pandas()
    score_rows = dataframe.to_dict(orient="records")

    detailed_rows: list[dict[str, Any]] = []
    for metadata, row, score_row in zip(metadata_rows, rows, score_rows, strict=True):
        detailed_rows.append(
            {
                **metadata,
                **row,
                **score_row,
            }
        )

    summary: dict[str, float] = {}
    for metric in ("faithfulness", "answer_relevancy", "context_precision", "context_recall"):
        values = [float(item[metric]) for item in score_rows if item.get(metric) is not None]
        summary[metric] = round(sum(values) / max(len(values), 1), 4)

    return {
        "judge_model": judge_config.judge_model,
        "embedding_model": judge_config.embedding_model,
        "case_count": len(rows),
        "summary": summary,
        "rows": detailed_rows,
        "dataset_rows": rows,
    }

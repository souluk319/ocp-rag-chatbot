from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

os.environ.setdefault("RAGAS_DO_NOT_TRACK", "true")

from openai import OpenAI
from ragas import EvaluationDataset, evaluate
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import llm_factory
from ragas.metrics._answer_relevance import AnswerRelevancy
from ragas.metrics._context_precision import ContextPrecision
from ragas.metrics._context_recall import ContextRecall
from ragas.metrics._faithfulness import Faithfulness
from langchain_openai import OpenAIEmbeddings as LangchainOpenAIEmbeddings

from ocp_rag_part1.settings import Settings

from .answerer import Part3Answerer
from .eval import evaluate_case, summarize_case_results


RAGAS_METRIC_ORDER = (
    "faithfulness",
    "answer_relevance",
    "context_precision",
    "context_recall",
)


@dataclass(slots=True)
class RagasJudgeConfig:
    model: str
    embedding_model: str
    temperature: float
    api_key: str
    base_url: str = ""

    def safe_dict(self) -> dict[str, Any]:
        return {
            "provider": "openai",
            "model": self.model,
            "embedding_model": self.embedding_model,
            "temperature": self.temperature,
            "base_url_configured": bool(self.base_url),
            "api_key_configured": bool(self.api_key),
        }


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def judge_config_from_settings(settings: Settings) -> RagasJudgeConfig:
    if not settings.ragas_judge_model:
        raise ValueError("RAGAS_JUDGE_MODEL must be configured")
    if not settings.ragas_judge_embedding_model:
        raise ValueError("RAGAS_JUDGE_EMBEDDING_MODEL must be configured")
    if not settings.ragas_openai_api_key:
        raise ValueError(
            "OPENAI_API_KEY or RAGAS_OPENAI_API_KEY must be configured for RAGAS judge runs"
        )
    return RagasJudgeConfig(
        model=settings.ragas_judge_model,
        embedding_model=settings.ragas_judge_embedding_model,
        temperature=settings.ragas_judge_temperature,
        api_key=settings.ragas_openai_api_key,
        base_url=settings.ragas_openai_base_url,
    )


def _build_openai_client(config: RagasJudgeConfig) -> OpenAI:
    client_kwargs: dict[str, Any] = {"api_key": config.api_key}
    if config.base_url:
        client_kwargs["base_url"] = config.base_url
    return OpenAI(**client_kwargs)


def build_ragas_metrics(config: RagasJudgeConfig) -> tuple[list[Any], list[str]]:
    client = _build_openai_client(config)
    judge_llm = llm_factory(
        config.model,
        provider="openai",
        client=client,
        temperature=config.temperature,
    )
    judge_embeddings = LangchainEmbeddingsWrapper(
        LangchainOpenAIEmbeddings(
            api_key=config.api_key,
            base_url=config.base_url or None,
            model=config.embedding_model,
        )
    )
    metrics = [
        Faithfulness(llm=judge_llm, name="faithfulness"),
        AnswerRelevancy(
            llm=judge_llm,
            embeddings=judge_embeddings,
            name="answer_relevance",
            strictness=1,
        ),
        ContextPrecision(
            llm=judge_llm,
            name="context_precision",
        ),
        ContextRecall(
            llm=judge_llm,
            name="context_recall",
        ),
    ]
    return metrics, [metric.name for metric in metrics]


def run_product_eval(
    answerer: Part3Answerer,
    cases: list[dict[str, Any]],
    *,
    top_k: int,
    candidate_k: int,
    max_context_chunks: int,
) -> list[dict[str, Any]]:
    details: list[dict[str, Any]] = []
    for case in cases:
        details.append(
            evaluate_case(
                answerer,
                case,
                top_k=top_k,
                candidate_k=candidate_k,
                max_context_chunks=max_context_chunks,
            )
        )
    return details


def _normalize_contexts(detail: dict[str, Any]) -> list[str]:
    contexts: list[str] = []
    for citation in detail.get("final_citations", []):
        excerpt = str(citation.get("excerpt", "")).strip()
        if excerpt:
            contexts.append(excerpt)
    return contexts


def build_ragas_samples(
    cases: list[dict[str, Any]],
    details: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    detail_by_id = {str(detail.get("id", "")): detail for detail in details}
    samples: list[dict[str, Any]] = []
    golden_cases: list[dict[str, Any]] = []
    product_rows: list[dict[str, Any]] = []

    for case in cases:
        case_id = str(case.get("id", ""))
        reference = str(case.get("reference_answer", "")).strip()
        if not reference:
            continue
        detail = detail_by_id.get(case_id)
        if detail is None:
            raise ValueError(f"missing product evaluation detail for case: {case_id}")

        sample = {
            "user_input": str(case["query"]),
            "response": str(detail.get("answer_text", "")).strip(),
            "retrieved_contexts": _normalize_contexts(detail),
            "reference": reference,
        }
        samples.append(sample)
        golden_cases.append(case)
        product_rows.append(detail)

    return samples, golden_cases, product_rows


def build_ragas_dataset(samples: list[dict[str, Any]]) -> EvaluationDataset:
    if not samples:
        raise ValueError("at least one golden case with reference_answer is required")
    return EvaluationDataset.from_list(samples)


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(parsed):
        return None
    return round(parsed, 4)


def summarize_ragas_rows(
    rows: list[dict[str, Any]],
    metric_names: list[str],
) -> dict[str, float]:
    summary: dict[str, float] = {}
    for metric_name in metric_names:
        values = [
            float(row[metric_name])
            for row in rows
            if row.get(metric_name) is not None
        ]
        summary[metric_name] = round(sum(values) / len(values), 4) if values else 0.0
    return summary


def evaluate_with_ragas(
    *,
    cases: list[dict[str, Any]],
    answerer: Part3Answerer,
    settings: Settings,
    top_k: int,
    candidate_k: int,
    max_context_chunks: int,
) -> dict[str, Any]:
    judge_config = judge_config_from_settings(settings)
    product_details = run_product_eval(
        answerer,
        cases,
        top_k=top_k,
        candidate_k=candidate_k,
        max_context_chunks=max_context_chunks,
    )
    product_summary = summarize_case_results(product_details)
    samples, golden_cases, ragas_product_rows = build_ragas_samples(cases, product_details)
    ragas_dataset = build_ragas_dataset(samples)
    metrics, metric_names = build_ragas_metrics(judge_config)
    ragas_result = evaluate(
        ragas_dataset,
        metrics=metrics,
        raise_exceptions=False,
        show_progress=True,
    )
    ragas_df = ragas_result.to_pandas()
    ragas_records = ragas_df.to_dict(orient="records")

    merged_rows: list[dict[str, Any]] = []
    for case, detail, ragas_row in zip(
        golden_cases,
        ragas_product_rows,
        ragas_records,
        strict=True,
    ):
        merged_row = {
            "id": case.get("id"),
            "mode": case.get("mode", "ops"),
            "query_type": case.get("query_type", "ops"),
            "question": case["query"],
            "reference_answer": case.get("reference_answer", ""),
            "rewritten_query": detail.get("rewritten_query", ""),
            "product_pass": detail.get("pass", False),
            "cited_books": detail.get("cited_books", []),
            "retrieved_books": detail.get("retrieved_books", []),
            "warnings": detail.get("warnings", []),
            "answer_text": detail.get("answer_text", ""),
            "final_citations": detail.get("final_citations", []),
            "retrieved_contexts": _normalize_contexts(detail),
        }
        for metric_name in metric_names:
            merged_row[metric_name] = _safe_float(ragas_row.get(metric_name))
        merged_rows.append(merged_row)

    return {
        "judge": judge_config.safe_dict(),
        "metric_names": metric_names,
        "case_count": len(merged_rows),
        "ragas_overall": summarize_ragas_rows(merged_rows, metric_names),
        "ragas_details": merged_rows,
        "product_eval": product_summary,
    }

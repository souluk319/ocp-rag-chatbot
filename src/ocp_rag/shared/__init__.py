"""Shared cross-layer utilities for the OCP RAG chatbot."""

from .io import read_jsonl
from ocp_rag.shared.settings import HIGH_VALUE_SLUGS, Settings, load_settings

__all__ = ["HIGH_VALUE_SLUGS", "Settings", "load_settings", "read_jsonl"]

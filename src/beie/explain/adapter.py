"""LLM adapter compatibility wrapper.

Re-exports core adapter functions from src/beie/llm/adapter.py.
"""

from __future__ import annotations

from beie.llm.adapter import (
    SYSTEM_PROMPT,
    explain,
    mask_api_key,
    test_connection,
)

__all__ = ["SYSTEM_PROMPT", "explain", "mask_api_key", "test_connection"]

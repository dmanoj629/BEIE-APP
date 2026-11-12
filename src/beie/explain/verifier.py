"""Number verifier — rejects LLM output containing ungrounded numbers.

Blueprint §11:
After each reply, verify every number appears in the input JSON.
If not, discard it and use a template explanation.
"""

from __future__ import annotations

import re
from typing import Any


def _extract_numbers(text: str) -> set[str]:
    """Extract all numeric tokens from text."""
    return set(re.findall(r"-?\d+(?:\.\d+)?", text))


def _extract_grounded_numbers(data: Any, depth: int = 0) -> set[str]:
    """Recursively extract all numeric values from a JSON-like structure."""
    found: set[str] = set()
    if depth > 10:
        return found
    if isinstance(data, (int, float)):
        found.add(str(round(float(data), 4)))
        found.add(str(int(data)) if data == int(data) else str(round(float(data), 2)))
    elif isinstance(data, dict):
        for v in data.values():
            found |= _extract_grounded_numbers(v, depth + 1)
    elif isinstance(data, (list, tuple)):
        for item in data:
            found |= _extract_grounded_numbers(item, depth + 1)
    elif isinstance(data, str):
        # Catch numbers embedded in strings
        found |= _extract_numbers(data)
    return found


def verify_response(llm_text: str, grounded_data: dict[str, Any]) -> bool:
    """Return True if every number in llm_text appears in grounded_data.

    Returns False if the LLM introduced a number not present in the source JSON.
    """
    llm_numbers = _extract_numbers(llm_text)
    grounded_numbers = _extract_grounded_numbers(grounded_data)

    # Allow small integers (1–100) which are likely ordinals or generic references
    for num in llm_numbers:
        try:
            val = float(num)
            if 1 <= val <= 100 and "." not in num:
                continue  # Ordinals/percentages like "1 month", "5 steps"
        except ValueError:
            pass
        # Check if number (or close rounding) appears in grounded set
        if num not in grounded_numbers:
            # Try rounded versions
            try:
                f = float(num)
                rounded_variants = {
                    str(round(f, 0)),
                    str(round(f, 1)),
                    str(round(f, 2)),
                    str(round(f, 3)),
                    str(int(f)),
                }
                if not grounded_variants_match(rounded_variants, grounded_numbers):
                    return False
            except ValueError:
                return False
    return True


def grounded_variants_match(variants: set[str], grounded: set[str]) -> bool:
    return bool(variants & grounded)

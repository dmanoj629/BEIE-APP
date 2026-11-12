"""Tests for AI integration adapter, masking, and connection testing."""

from __future__ import annotations

from beie.llm.adapter import (
    explain,
    mask_api_key,
    test_connection as ping_api_connection,
)


def test_mask_api_key_empty():
    assert mask_api_key("") == ""
    assert mask_api_key("   ") == ""


def test_mask_api_key_short():
    assert mask_api_key("12345") == "••••••••"


def test_mask_api_key_standard():
    masked = mask_api_key("sk-1234567890abcdef")
    assert masked.startswith("sk-1")
    assert masked.endswith("cdef")
    assert "••••••••" in masked


def test_connection_empty_key():
    res = ping_api_connection("gemini", "")
    assert res["status"] == "INVALID_CREDENTIALS"
    assert "empty" in res["message"].lower()


def test_connection_invalid_key():
    res = ping_api_connection("gemini", "INVALID_TEST_KEY_99999999")
    # Should fail with INVALID_CREDENTIALS or PROVIDER_UNAVAILABLE
    assert res["status"] in ("INVALID_CREDENTIALS", "PROVIDER_UNAVAILABLE", "NETWORK_FAILURE")


def test_explain_fallback_without_key():
    result = explain(
        domain="energy",
        result_json={"P50": 0.52, "P10": 0.20, "P90": 0.85},
        lang="en",
        api_key="",
    )
    assert result["source"] == "template"
    assert len(result["text"]) > 0
    assert "notice" in result


def test_explain_multilingual_fallback():
    for lang in ("en", "kn", "hi"):
        res = explain(
            domain="energy",
            result_json={"P50": 0.52, "P10": 0.20, "P90": 0.85},
            lang=lang,
            api_key="",
        )
        assert res["lang"] == lang
        assert len(res["text"]) > 0

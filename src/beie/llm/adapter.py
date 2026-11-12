"""BEIE AI Integration Engine & LLM Adapter.

Implements:
- Google Gemini and OpenAI provider adapters.
- Real-time connection testing without user data transmission.
- Strict numerical and provenance verification.
- Fallback to verified multilingual deterministic templates.
- Caching of repeated queries.
- Key masking and secure storage helpers.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.request
from typing import Any

from beie.explain.templates import fill_template
from beie.explain.verifier import verify_response

_CACHE: dict[str, str] = {}


def mask_api_key(key: str) -> str:
    """Mask sensitive API key for safe display (e.g., 'sk-...4a12')."""
    k = (key or "").strip()
    if not k:
        return ""
    if len(k) <= 8:
        return "••••••••"
    return f"{k[:4]}••••••••{k[-4:]}"


def test_connection(
    provider: str, api_key: str, model: str | None = None
) -> dict[str, Any]:
    """Test AI API credentials with a lightweight ping request.

    Does not send personal profile data.
    Returns status: CONNECTED | INVALID_CREDENTIALS | NETWORK_FAILURE | RATE_LIMITED | PROVIDER_UNAVAILABLE | UNSUPPORTED_MODEL.
    """
    key = (api_key or "").strip()
    if not key:
        return {
            "status": "INVALID_CREDENTIALS",
            "message": "API key cannot be empty.",
            "latency_ms": 0.0,
        }

    prov = (provider or "gemini").lower()
    t0 = time.perf_counter()

    if prov == "gemini":
        target_model = model or "gemini-2.5-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{target_model}:generateContent?key={key}"
        body = {
            "contents": [{"parts": [{"text": "Reply with 'CONNECTED'"}]}],
            "generationConfig": {"maxOutputTokens": 10, "temperature": 0.0},
        }
    else:
        # OpenAI
        target_model = model or "gpt-4o-mini"
        url = "https://api.openai.com/v1/chat/completions"
        body = {
            "model": target_model,
            "messages": [{"role": "user", "content": "Reply with 'CONNECTED'"}],
            "max_tokens": 10,
            "temperature": 0.0,
        }

    data = json.dumps(body).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if prov != "gemini":
        headers["Authorization"] = f"Bearer {key}"

    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            raw_res = json.loads(resp.read().decode("utf-8"))
            elapsed = (time.perf_counter() - t0) * 1000
            return {
                "status": "CONNECTED",
                "message": f"Successfully connected to {prov.title()} ({target_model}) in {elapsed:.0f}ms.",
                "latency_ms": round(elapsed, 1),
            }
    except urllib.error.HTTPError as exc:
        elapsed = (time.perf_counter() - t0) * 1000
        code = exc.code
        err_msg = ""
        try:
            err_msg = exc.read().decode("utf-8", errors="ignore")
        except Exception:
            pass

        if code in (401, 403):
            return {
                "status": "INVALID_CREDENTIALS",
                "message": f"Authentication failed (HTTP {code}): Invalid API key.",
                "latency_ms": round(elapsed, 1),
            }
        elif code == 429:
            return {
                "status": "RATE_LIMITED",
                "message": "Rate limit exceeded for this API key. Try again later.",
                "latency_ms": round(elapsed, 1),
            }
        elif code == 404 or "not found" in err_msg.lower():
            return {
                "status": "UNSUPPORTED_MODEL",
                "message": f"Model '{target_model}' not found or unsupported by this provider.",
                "latency_ms": round(elapsed, 1),
            }
        else:
            return {
                "status": "PROVIDER_UNAVAILABLE",
                "message": f"Provider returned HTTP error {code}: {exc.reason}",
                "latency_ms": round(elapsed, 1),
            }
    except urllib.error.URLError as exc:
        elapsed = (time.perf_counter() - t0) * 1000
        return {
            "status": "NETWORK_FAILURE",
            "message": f"Network failure: Unable to reach provider server ({exc.reason}).",
            "latency_ms": round(elapsed, 1),
        }
    except Exception as exc:
        elapsed = (time.perf_counter() - t0) * 1000
        return {
            "status": "PROVIDER_UNAVAILABLE",
            "message": f"Unexpected connection error: {exc}",
            "latency_ms": round(elapsed, 1),
        }


SYSTEM_PROMPT = """You are the AI Economic Analyst for the Bharat Economic Intelligence Engine (BEIE).
You will receive structured JSON scenario results containing computed economic metrics, sources, and assumptions.
Your role: explain the results clearly to an Indian citizen or business in the specified language (English, Kannada, or Hindi).

STRICT NON-NEGOTIABLE RULES:
1. ONLY use numbers that exist in the supplied JSON. NEVER invent, estimate, extrapolate, or fabricate new numerical statistics.
2. DO NOT make personal stock recommendations or issue buy/sell investment calls.
3. Clearly state whether the output is a historical observation, a scenario simulation, or an assumption.
4. Include:
   - 1-line plain-language summary
   - User-specific impact
   - Why it happens (economic transmission chain)
   - Monte Carlo uncertainty range (P10/P50/P90)
   - Sources & assumptions
5. If the numbers cannot be strictly grounded in the provided JSON, reply with exactly: TEMPLATE_FALLBACK
"""


def _cache_key(payload: dict[str, Any]) -> str:
    return hashlib.md5(
        json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()


def explain(
    domain: str,
    result_json: dict[str, Any],
    lang: str = "en",
    template_ctx: dict[str, Any] | None = None,
    api_key: str | None = None,
    model: str | None = None,
    provider: str | None = None,
) -> dict[str, str]:
    """Generate a plain-language explanation of structured economic results.

    Verifies numbers against the input JSON. Falls back to verified templates on error or hallucination.
    """
    key = api_key or os.environ.get("LLM_API_KEY", "")
    target_model = model or os.environ.get("LLM_MODEL", "gemini-2.5-flash")
    prov = (
        provider
        or os.environ.get("LLM_PROVIDER")
        or ("openai" if "gpt" in target_model.lower() else "gemini")
    )

    if not key:
        return _template_fallback(
            domain, lang, template_ctx or {}, reason="LLM_API_KEY not configured"
        )

    # Sanitize payload: never send private personal data
    safe_result = {
        "domain": domain,
        "summary": result_json.get("summary"),
        "uncertainty": result_json.get("uncertainty"),
        "assumptions": result_json.get("assumptions"),
        "risks": result_json.get("risks"),
        "observations": [
            {
                "indicator": o.get("indicator"),
                "value": o.get("value"),
                "unit": o.get("unit"),
            }
            for o in result_json.get("observations", [])
            if isinstance(o, dict)
        ],
    }

    payload = {
        "result": safe_result,
        "language": lang,
        "domain": domain,
    }
    ck = _cache_key(payload)
    if ck in _CACHE:
        return {
            "text": _CACHE[ck],
            "source": f"{prov}_cache",
            "lang": lang,
            "notice": _notice(prov, target_model),
        }

    try:
        llm_text = _call_llm_api(key, prov, target_model, payload, max_tokens=350)
        if llm_text.strip() == "TEMPLATE_FALLBACK":
            return _template_fallback(
                domain, lang, template_ctx or {}, reason="LLM requested fallback"
            )

        # Number verification gate: reject hallucinated statistics
        if not verify_response(llm_text, safe_result):
            return _template_fallback(
                domain,
                lang,
                template_ctx or {},
                reason="Numerical verification alert: ungrounded number detected",
            )

        _CACHE[ck] = llm_text
        return {
            "text": llm_text,
            "source": prov,
            "lang": lang,
            "notice": _notice(prov, target_model),
        }
    except Exception as exc:
        return _template_fallback(
            domain, lang, template_ctx or {}, reason=f"AI connection error: {exc}"
        )


def _call_llm_api(
    api_key: str,
    provider: str,
    model: str,
    payload: dict[str, Any],
    max_tokens: int = 350,
) -> str:
    """Execute raw LLM API call."""
    prov = provider.lower()
    if prov == "gemini":
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        body = {
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": [
                {
                    "parts": [
                        {"text": json.dumps(payload, default=str, ensure_ascii=False)}
                    ]
                }
            ],
            "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.1},
        }
        headers = {"Content-Type": "application/json"}
    else:
        url = "https://api.openai.com/v1/chat/completions"
        body = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": json.dumps(payload, default=str, ensure_ascii=False),
                },
            ],
            "max_tokens": max_tokens,
            "temperature": 0.1,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=12) as resp:
        rdata = json.loads(resp.read().decode("utf-8"))

    if prov == "gemini":
        return rdata["candidates"][0]["content"]["parts"][0]["text"]
    return rdata["choices"][0]["message"]["content"]


def _template_fallback(
    domain: str, lang: str, ctx: dict[str, Any], reason: str
) -> dict[str, str]:
    text = fill_template(domain, lang, ctx)
    return {
        "text": text,
        "source": "template",
        "lang": lang,
        "reason": reason,
        "notice": _notice(provider="template", model="deterministic"),
    }


def _notice(provider: str = "ai", model: str = "") -> str:
    if provider == "template":
        return (
            "Explanation generated from BEIE's deterministic multilingual template library. "
            "All numbers are verified against official economic data."
        )
    return (
        f"Explanation interpreted by {provider.title()} ({model}) from validated scenario outputs. "
        "All figures verified against computed results. Informational only — not financial advice."
    )

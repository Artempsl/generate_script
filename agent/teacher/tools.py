"""
Tools for the Teacher pipeline.

Three tools:
1. generate_teacher_outline_tool — lesson arc outline via GPT-4o-mini
2. generate_teacher_script_tool  — educational narrative script via GPT-4o-mini
3. fact_check_tool               — fact-checking via Facticity API (or graceful skip)
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from agent.config import FACTICITY_API, OPENAI_MODEL, OUTLINE_TEMPERATURE, SCRIPT_TEMPERATURE, MAX_OUTLINE_TOKENS
from agent.teacher.prompts import TEACHER_OUTLINE_PROMPT, TEACHER_SCRIPT_PROMPT, FACT_CORRECTION_PROMPT

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Shared LLM helpers (thin wrappers — avoid import cycle with agent.tools)
# ---------------------------------------------------------------------------

def _get_llm(temperature: float, max_tokens: Optional[int] = None):
    """Return a ChatOpenAI instance with the given settings."""
    from langchain_openai import ChatOpenAI
    kwargs: Dict[str, Any] = {
        "model": OPENAI_MODEL,
        "temperature": temperature,
        "api_key": os.environ.get("OPENAI_API_KEY", ""),
    }
    if max_tokens:
        kwargs["max_tokens"] = max_tokens
    return ChatOpenAI(**kwargs)


def _calculate_max_tokens(target_chars: int) -> int:
    """1 token ≈ 4 chars; add 20% buffer."""
    return min(int(target_chars / 4 * 1.2) + 500, 16000)


# =============================================================================
# TOOL 1 — GENERATE TEACHER OUTLINE
# =============================================================================

@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=10))
def generate_teacher_outline_tool(
    topic: str,
    description: str,
    style: str,
    duration: int,
    language: str,
    target_chars: int,
    reasoning_strategy: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate a lesson outline for the teacher pipeline.

    Returns:
        {"success": bool, "outline": str, "tokens_used": int, "error": Optional[str]}
    """
    try:
        from langchain_core.messages import HumanMessage, SystemMessage

        lang_instruction = "Write in Russian" if language == "ru" else "Write in English"

        strategy_note = ""
        if reasoning_strategy:
            strategy_note = f"\n\nSTRATEGIC DIRECTION:\n{reasoning_strategy}\n\nUse this approach in your outline."

        system_prompt = TEACHER_OUTLINE_PROMPT.format(
            style=style,
            topic=topic,
            lang_instruction=lang_instruction,
            description=description,
            duration=duration,
            target_chars=target_chars,
        ) + strategy_note

        user_prompt = (
            f"Create a detailed lesson outline for a {duration}-minute {style} video "
            f"about {topic}.\n\nLesson description / audience: {description}"
        )

        llm = _get_llm(temperature=OUTLINE_TEMPERATURE, max_tokens=MAX_OUTLINE_TOKENS)
        response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
        outline_text = response.content

        tokens_used = (len(system_prompt) + len(user_prompt) + len(outline_text)) // 4

        return {"success": True, "outline": outline_text, "tokens_used": tokens_used, "error": None}

    except Exception as exc:
        return {"success": False, "outline": "", "tokens_used": 0, "error": str(exc)}


# =============================================================================
# TOOL 2 — GENERATE TEACHER SCRIPT
# =============================================================================

@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=10))
def generate_teacher_script_tool(
    outline: str,
    topic: str,
    description: str,
    style: str,
    duration: int,
    language: str,
    target_chars: int,
    iteration: int = 0,
    adjustment_instruction: Optional[str] = None,
    fact_correction: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate a full educational script from the lesson outline.

    Returns:
        {"success": bool, "script": str, "char_count": int, "tokens_used": int, "error": Optional[str]}
    """
    try:
        from langchain_core.messages import HumanMessage, SystemMessage

        lang_instruction = "Write in Russian" if language == "ru" else "Write in English"

        iteration_note = f"\n\n(Iteration {iteration + 1})" if iteration > 0 else ""
        adjustment_note = f"\n\nLENGTH ADJUSTMENT NEEDED:\n{adjustment_instruction}" if adjustment_instruction else ""
        fact_correction_note = (
            f"\n\nFACT CORRECTION REQUIRED:\n{fact_correction}" if fact_correction else ""
        )

        system_prompt = TEACHER_SCRIPT_PROMPT.format(
            style=style,
            topic=topic,
            lang_instruction=lang_instruction,
            description=description,
            duration=duration,
            target_chars=target_chars,
            iteration_note=iteration_note,
            adjustment_note=adjustment_note,
            fact_correction_note=fact_correction_note,
        )

        user_prompt = (
            f"Topic: {topic}\nStyle: {style}\nAudience/context: {description}\n\n"
            f"Outline:\n{outline}\n\n"
            f"Write the complete {duration}-minute educational script. "
            f"Aim for exactly {target_chars:,} characters."
        )

        max_tokens = _calculate_max_tokens(target_chars)
        llm = _get_llm(temperature=SCRIPT_TEMPERATURE, max_tokens=max_tokens)
        response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
        script_text = response.content
        char_count = len(script_text)

        tokens_used = (len(system_prompt) + len(user_prompt) + len(script_text)) // 4

        return {
            "success": True,
            "script": script_text,
            "char_count": char_count,
            "tokens_used": tokens_used,
            "error": None,
        }

    except Exception as exc:
        return {"success": False, "script": "", "char_count": 0, "tokens_used": 0, "error": str(exc)}


# =============================================================================
# TOOL 3 — FACT CHECK (two-stage: LLM extraction → Facticity API verification)
# =============================================================================

_FACTICITY_BASE_URL = "https://api.facticity.ai"

_CLAIM_EXTRACTION_PROMPT = """\
You are a fact-checking assistant. Read the educational script below and extract \
every specific factual claim that contains a verifiable number, date, formula, \
or measurable quantity.

Rules:
- Include only claims that have an exact number, year, formula, or measurement
- Do NOT include vague statements like "many scientists believe..." or "gravity is important"
- Each claim must be a self-contained sentence or phrase from the script
- Return a JSON array of strings. Example:
  ["Newton published his laws of motion in 1687.",
   "The formula for gravitational force is F = GMm/r\u00b2.",
   "Light travels at 299,792 km/s."]
- If there are no verifiable numerical claims, return an empty array: []

Script:
\"\"\"
{script}
\"\"\"

Return ONLY the JSON array, no explanation."""


def _extract_claims_with_llm(script: str) -> List[str]:
    """Stage B: GPT-4o-mini extracts verifiable factual claims from the script."""
    try:
        from langchain_core.messages import HumanMessage

        llm = _get_llm(temperature=0.0, max_tokens=1000)
        prompt = _CLAIM_EXTRACTION_PROMPT.format(script=script)
        response = llm.invoke([HumanMessage(content=prompt)])
        raw = response.content.strip()

        # Strip markdown code fences if present
        if raw.startswith("```"):
            parts = raw.split("```")
            raw = parts[1] if len(parts) > 1 else raw
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        claims = json.loads(raw)
        if not isinstance(claims, list):
            return []
        return [str(c) for c in claims if c]

    except Exception as exc:
        logger.warning(f"LLM claim extraction failed: {exc}")
        return []


def _facticity_fact_check(claim: str, api_key: str) -> Dict[str, Any]:
    """Stage A: Submit a single claim to the Facticity API (sync mode)."""
    headers = {"Content-Type": "application/json", "x-api-key": api_key}

    try:
        resp = requests.post(
            f"{_FACTICITY_BASE_URL}/fact-check",
            json={"query": claim, "timeout": 60, "mode": "sync"},
            headers=headers,
            timeout=90,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        logger.warning(f"Facticity submit failed for '{claim[:60]}': {exc}")
        return {
            "claim": claim, "verdict": "unknown", "confidence": None,
            "source_url": None, "requires_manual_check": True,
            "manual_check_reason": "API error during submission",
        }

    logger.debug(f"[FACT-CHECK] Raw Facticity response for '{claim[:60]}': {data}")

    # Facticity response schema:
    #   "Classification": "True" | "False" | "Misleading" | ...
    #   "overall_assessment": str  (detailed explanation)
    #   "evidence": dict {url: snippet}
    #   "sources": list | dict
    #   "input": str  (echoed query)
    raw_verdict = (
        data.get("Classification")
        or data.get("verdict")
        or data.get("result")
        or data.get("label")
        or data.get("status", "unknown")
    )
    v = str(raw_verdict).lower()

    known_verdicts = {"true", "false", "incorrect", "misleading", "unverifiable"}
    # "unverifiable" means the API could not confirm or deny — treat as manual check
    requires_manual = v not in known_verdicts or v == "unverifiable"
    manual_reason = None
    if v not in known_verdicts:
        manual_reason = f"Unrecognized verdict: {raw_verdict!r}"
    elif v == "unverifiable":
        manual_reason = "Claim could not be verified by the API"

    # Pick a representative source URL from evidence dict
    source_url = None
    evidence = data.get("evidence") or {}
    if isinstance(evidence, dict) and evidence:
        source_url = next(iter(evidence))
    elif isinstance(data.get("sources"), list) and data["sources"]:
        first = data["sources"][0]
        source_url = first.get("url") or first.get("link") if isinstance(first, dict) else None

    return {
        "claim": claim,
        "verdict": v,
        "confidence": data.get("confidence") or data.get("score"),
        "source_url": source_url,
        "overall_assessment": data.get("overall_assessment"),
        "requires_manual_check": requires_manual,
        "manual_check_reason": manual_reason,
    }


def fact_check_tool(script: str) -> Dict[str, Any]:
    """
    Two-stage fact-checking:

    Stage B (always runs): GPT-4o-mini extracts verifiable claims with exact
        numbers / dates / formulas from the script.
    Stage A (only if FACTICITY_API key is set): each claim is verified via
        the Facticity API (async polling).

    If no API key is configured, claims are returned with verdict="not_checked"
    so the pipeline still knows what factual assertions exist in the script.

    Returns:
        {
            "passed": bool,
            "citations": List[Dict],   # [{claim, verdict, confidence, source_url}]
            "correction_instruction": str,
        }
    """
    api_key = FACTICITY_API

    # ── Stage B: LLM claim extraction (always) ────────────────────────────────
    logger.info("[FACT-CHECK] Stage B: extracting verifiable claims with LLM...")
    claims = _extract_claims_with_llm(script)
    logger.info(f"[FACT-CHECK] Extracted {len(claims)} claim(s): {claims}")

    if not claims:
        logger.info("[FACT-CHECK] No verifiable numerical claims found — auto-pass")
        return {"passed": True, "citations": [], "correction_instruction": ""}

    # ── Deduplicate claims (LLM may return the same claim multiple times) ──────
    seen_keys: set = set()
    unique_claims: List[str] = []
    for c in claims:
        key = c[:80].lower().strip()
        if key not in seen_keys:
            seen_keys.add(key)
            unique_claims.append(c)
    if len(unique_claims) < len(claims):
        logger.info(f"[FACT-CHECK] Deduplicated: {len(claims)} → {len(unique_claims)} claim(s)")
    claims = unique_claims

    # ── No API key: return claims as not_checked ───────────────────────────────
    if not api_key:
        logger.info("[FACT-CHECK] FACTICITY_API not set — returning claims as not_checked")
        citations = [
            {
                "claim": c, "verdict": "not_checked", "confidence": None,
                "source_url": None, "requires_manual_check": True,
                "manual_check_reason": "FACTICITY_API key not configured",
            }
            for c in claims
        ]
        return {"passed": True, "citations": citations, "correction_instruction": ""}

    # ── Stage A: Facticity API verification ───────────────────────────────────
    logger.info(f"[FACT-CHECK] Stage A: verifying {len(claims)} claim(s) via Facticity API...")
    citations: List[Dict[str, Any]] = []
    for claim in claims:
        result = _facticity_fact_check(claim, api_key)
        citations.append(result)
        logger.info(f"  → '{claim[:60]}' → verdict={result['verdict']}")

    failed = [
        c for c in citations
        if str(c.get("verdict", "")).lower() in ("false", "incorrect", "misleading")
    ]
    passed = len(failed) == 0

    correction_instruction = ""
    if not passed:
        failed_lines = "\n".join(
            f'- "{c["claim"]}" (verdict: {c["verdict"]}, confidence: {c.get("confidence", "n/a")})'
            for c in failed
        )
        correction_instruction = FACT_CORRECTION_PROMPT.format(failed_claims=failed_lines)

    return {"passed": passed, "citations": citations, "correction_instruction": correction_instruction}

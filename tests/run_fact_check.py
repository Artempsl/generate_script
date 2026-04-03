"""
Fact-check test runner.

Loads the sample script (tests/sample_script_with_errors.txt), which contains several
deliberate factual errors, then runs it through the same fact_check_tool used in the
teacher pipeline.

Deliberate errors in the sample script:
  - Speed of light stated as 200,000 km/s  (correct: ~299,792 km/s)
  - Newton's laws published in 1700        (correct: Principia 1687)
  - Gravitational acceleration 8.5 m/s²   (correct: ~9.8 m/s²)
  - Atomic number of gold stated as 60     (correct: 79)
  - Water boils at 90 °C at sea level      (correct: 100 °C)
  - Einstein won Nobel Prize for Relativity (he actually won for Photoelectric Effect)

Usage:
    python tests/run_fact_check.py
"""

import sys
import json
from pathlib import Path

# Ensure project root is on the path so agent.* imports work
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agent.teacher.tools import fact_check_tool  # noqa: E402


SCRIPT_PATH = Path(__file__).parent / "sample_script_with_errors.txt"

SEPARATOR = "=" * 70


def main():
    print(SEPARATOR)
    print("FACT-CHECK PIPELINE TEST")
    print(f"Script file: {SCRIPT_PATH.name}")
    print(SEPARATOR)

    script_text = SCRIPT_PATH.read_text(encoding="utf-8")
    print(f"\nScript preview ({len(script_text)} chars):\n")
    print(script_text[:300].rstrip(), "...\n")

    print(SEPARATOR)
    print("Running fact_check_tool (Stage B → Stage A) ...\n")

    result = fact_check_tool(script_text)

    passed = result.get("passed", False)
    citations = result.get("citations", [])
    correction_instruction = result.get("correction_instruction", "")

    print(f"PASSED: {passed}")
    print(f"CLAIMS FOUND: {len(citations)}")
    print()

    if not citations:
        print("No verifiable claims were extracted from the script.")
        return

    for i, c in enumerate(citations, 1):
        verdict = c.get("verdict", "?")
        requires_manual = c.get("requires_manual_check", False)
        reason = c.get("manual_check_reason") or ""
        confidence = c.get("confidence")
        source = c.get("source_url") or "—"

        # Human-friendly verdict label
        verdict_label = {
            "true":        "✅ TRUE",
            "false":       "❌ FALSE",
            "incorrect":   "❌ INCORRECT",
            "misleading":  "⚠️  MISLEADING",
            "unknown":     "❓ UNKNOWN",
            "not_checked": "⏭  NOT CHECKED",
        }.get(verdict.lower(), f"❓ {verdict.upper()}")

        flag = "  🔎 REQUIRES MANUAL CHECK" if requires_manual else ""
        assessment = c.get("overall_assessment") or ""

        print(f"[{i}] {verdict_label}{flag}")
        print(f"     Claim      : {c.get('claim', '')}")
        if confidence is not None:
            print(f"     Confidence : {confidence}")
        if source != "—":
            print(f"     Source     : {source}")
        if reason:
            print(f"     Reason     : {reason}")
        if assessment:
            # Show first 200 chars of the assessment
            short = assessment[:200].replace("\n", " ")
            print(f"     Assessment : {short}{'...' if len(assessment) > 200 else ''}")
        print()

    if correction_instruction:
        print(SEPARATOR)
        print("CORRECTION INSTRUCTION:")
        print(correction_instruction)
        print()

    print(SEPARATOR)
    print("RAW JSON OUTPUT:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(SEPARATOR)


if __name__ == "__main__":
    main()

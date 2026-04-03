"""
Single-claim test: sends ONE claim through _facticity_fact_check and writes result to
tests/single_claim_result.json so it can be read without terminal capture issues.

Claim tested: "Isaac Newton published his laws of motion in 1700."
Correct answer: 1687 (Principia Mathematica) — so Facticity should return False.
"""
import sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent.teacher.tools import _facticity_fact_check
from agent.config import FACTICITY_API

OUT = Path(__file__).parent / "single_claim_result.json"

claim = "Isaac Newton published his laws of motion in 1700."
print(f"Claim: {claim}", flush=True)
print(f"API key set: {bool(FACTICITY_API)}", flush=True)

result = _facticity_fact_check(claim, FACTICITY_API)

OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Done. Result written to: {OUT.name}", flush=True)
print(f"verdict      : {result['verdict']}", flush=True)
print(f"req_manual   : {result['requires_manual_check']}", flush=True)
assessment = str(result.get("overall_assessment") or "")
print(f"assessment   : {assessment[:200]}", flush=True)

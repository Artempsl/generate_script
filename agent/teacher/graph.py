"""
Teacher pipeline LangGraph StateGraph.

12 nodes (no web_search compared to YouTube's 13 nodes).

Reused from agent.graph:
  create_project_node, retrieve_node, synthesize_node, reasoning_node,
  validate_node, regenerate_node, segment_script_node, generate_audio_node,
  extract_entities_node, save_execution_report_node, should_regenerate

New nodes (defined here):
  generate_teacher_outline_node   — lesson arc outline
  generate_teacher_script_node    — educational script using teacher prompts
  fact_check_node                 — fact-check via Facticity API
  regenerate_after_factcheck_node — re-generate script with fact corrections

Graph flow:
  START → create_project → retrieve → synthesize → reasoning
        → generate_teacher_outline → generate_teacher_script
        → validate ↔ regenerate (max 3)
        → fact_check ↔ regenerate_after_factcheck (max 2)
        → segment_script → generate_audio → extract_entities
        → generate_images → generate_video → save_execution_report → END
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Literal

from langgraph.graph import END, StateGraph

from agent.graph import (
    GraphState,
    create_project_node,
    extract_entities_node,
    generate_audio_node,
    generate_images_node,
    generate_video_node,
    reasoning_node,
    regenerate_node,
    retrieve_node,
    save_execution_report_node,
    segment_script_node,
    should_regenerate,
    synthesize_node,
    validate_node,
)
from agent.models import AgentState
from agent.teacher.tools import (
    fact_check_tool,
    generate_teacher_outline_tool,
    generate_teacher_script_tool,
)

logger = logging.getLogger(__name__)

MAX_FACT_CHECK_ITERATIONS = 2


# =============================================================================
# NEW NODE 1 — GENERATE TEACHER OUTLINE
# =============================================================================

def generate_teacher_outline_node(state: AgentState) -> AgentState:
    """
    Generate a lesson outline using the teacher-specific outline prompt.
    Updates: outline, tokens_used, reasoning_trace
    """
    logger.info("[TEACHER] Entering generate_teacher_outline_node")

    result = generate_teacher_outline_tool(
        topic=state.get("topic", state.get("genre", "")),
        description=state.get("idea", ""),
        style=state.get("style", "Narrative / Story-driven"),
        duration=state["duration"],
        language=state["language"],
        target_chars=state["target_chars"],
        reasoning_strategy=str(state.get("reasoning_strategy", "")) or None,
    )

    step = {
        "step": len(state["reasoning_trace"]) + 1,
        "action": "generate_teacher_outline",
        "result": f"Outline generated ({len(result.get('outline', ''))} chars)"
        if result["success"]
        else f"Error: {result.get('error')}",
        "tokens_used": result.get("tokens_used", 0),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    updates: AgentState = {
        "outline": result.get("outline", ""),
        "tokens_used": state["tokens_used"] + result.get("tokens_used", 0),
        "reasoning_trace": [step],
    }

    if not result["success"]:
        updates["error"] = f"Teacher outline generation failed: {result.get('error')}"

    return updates


# =============================================================================
# NEW NODE 2 — GENERATE TEACHER SCRIPT
# =============================================================================

def generate_teacher_script_node(state: AgentState) -> AgentState:
    """
    Generate a full educational script using the teacher-specific script prompt.
    Updates: script, char_count, tokens_used, reasoning_trace
    """
    logger.info("[TEACHER] Entering generate_teacher_script_node")

    result = generate_teacher_script_tool(
        outline=state["outline"],
        topic=state.get("topic", state.get("genre", "")),
        description=state.get("idea", ""),
        style=state.get("style", "Narrative / Story-driven"),
        duration=state["duration"],
        language=state["language"],
        target_chars=state["target_chars"],
        iteration=state.get("iteration", 0),
    )

    step = {
        "step": len(state["reasoning_trace"]) + 1,
        "action": "generate_teacher_script",
        "result": f"Script generated ({result.get('char_count', 0):,} chars)"
        if result["success"]
        else f"Error: {result.get('error')}",
        "tokens_used": result.get("tokens_used", 0),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    updates: AgentState = {
        "script": result.get("script", ""),
        "char_count": result.get("char_count", 0),
        "tokens_used": state["tokens_used"] + result.get("tokens_used", 0),
        "reasoning_trace": [step],
    }

    if not result["success"]:
        updates["error"] = f"Teacher script generation failed: {result.get('error')}"

    return updates


# =============================================================================
# NEW NODE 3 — FACT CHECK
# =============================================================================

def fact_check_node(state: AgentState) -> AgentState:
    """
    Post the script to the Facticity API and store results.
    Updates: fact_check_result, fact_check_citations, fact_check_passed,
             fact_check_iteration, fact_check_correction, reasoning_trace
    """
    logger.info("[TEACHER] Entering fact_check_node")

    result = fact_check_tool(script=state.get("script", ""))

    new_iteration = state.get("fact_check_iteration", 0) + 1

    # Accumulate per-iteration snapshot for final report
    snapshots = list(state.get("fact_check_snapshots", []))
    snapshots.append({
        "iteration": new_iteration,
        "citations": result.get("citations", []),
    })

    step = {
        "step": len(state["reasoning_trace"]) + 1,
        "action": "fact_check",
        "result": f"passed={result['passed']}, citations={len(result.get('citations', []))}",
        "tokens_used": 0,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    return {
        "fact_check_result": result,
        "fact_check_citations": result.get("citations", []),
        "fact_check_passed": result["passed"],
        "fact_check_iteration": new_iteration,
        "fact_check_correction": result.get("correction_instruction", ""),
        "fact_check_snapshots": snapshots,
        "reasoning_trace": [step],
    }


# =============================================================================
# NEW NODE 4 — REGENERATE AFTER FACTCHECK
# =============================================================================

def regenerate_after_factcheck_node(state: AgentState) -> AgentState:
    """
    Re-generate the script incorporating fact-check corrections.
    Updates: script, char_count, tokens_used, validation_passed, reasoning_trace
    """
    logger.info("[TEACHER] Entering regenerate_after_factcheck_node")

    result = generate_teacher_script_tool(
        outline=state["outline"],
        topic=state.get("topic", state.get("genre", "")),
        description=state.get("idea", ""),
        style=state.get("style", "Narrative / Story-driven"),
        duration=state["duration"],
        language=state["language"],
        target_chars=state["target_chars"],
        iteration=state.get("iteration", 0),
        fact_correction=state.get("fact_check_correction", ""),
    )

    step = {
        "step": len(state["reasoning_trace"]) + 1,
        "action": "regenerate_after_factcheck",
        "result": f"Corrected script ({result.get('char_count', 0):,} chars)"
        if result["success"]
        else f"Error: {result.get('error')}",
        "tokens_used": result.get("tokens_used", 0),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    updates: AgentState = {
        "script": result.get("script", ""),
        "char_count": result.get("char_count", 0),
        "tokens_used": state["tokens_used"] + result.get("tokens_used", 0),
        # Reset validation so the corrected script can be re-checked on next loop
        "validation_passed": False,
        "reasoning_trace": [step],
    }

    if not result["success"]:
        updates["error"] = f"Fact-check regeneration failed: {result.get('error')}"

    return updates


# =============================================================================
# CONDITIONAL — FACT CHECK PASS/FAIL
# =============================================================================

def should_pass_factcheck(state: AgentState) -> Literal["segment_script", "regenerate_after_factcheck"]:
    """
    Route to segment_script if fact-check passed or max iterations reached.
    Otherwise route to regenerate_after_factcheck.
    """
    if state.get("fact_check_passed"):
        return "segment_script"
    if state.get("fact_check_iteration", 0) >= MAX_FACT_CHECK_ITERATIONS:
        logger.warning(
            "[TEACHER] Max fact-check iterations reached — proceeding with unverified script"
        )
        return "segment_script"
    return "regenerate_after_factcheck"


# =============================================================================
# GRAPH DEFINITION
# =============================================================================

def create_teacher_graph():
    """
    Build and compile the teacher LangGraph StateGraph (12 nodes).

    Returns:
        Compiled graph ready for execution.
    """
    workflow = StateGraph(GraphState)

    # ── Reused nodes ───────────────────────────────────────────────────────────
    workflow.add_node("create_project", create_project_node)
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("synthesize", synthesize_node)
    workflow.add_node("reasoning", reasoning_node)
    workflow.add_node("validate", validate_node)
    workflow.add_node("regenerate", regenerate_node)
    workflow.add_node("segment_script", segment_script_node)
    workflow.add_node("generate_audio", generate_audio_node)
    workflow.add_node("extract_entities", extract_entities_node)
    workflow.add_node("generate_images", generate_images_node)
    workflow.add_node("generate_video", generate_video_node)
    workflow.add_node("save_execution_report", save_execution_report_node)

    # ── New teacher nodes ──────────────────────────────────────────────────────
    workflow.add_node("generate_teacher_outline", generate_teacher_outline_node)
    workflow.add_node("generate_teacher_script", generate_teacher_script_node)
    workflow.add_node("fact_check", fact_check_node)
    workflow.add_node("regenerate_after_factcheck", regenerate_after_factcheck_node)

    # ── Entry point ────────────────────────────────────────────────────────────
    workflow.set_entry_point("create_project")

    # ── Sequential edges ───────────────────────────────────────────────────────
    workflow.add_edge("create_project", "retrieve")
    # (no web_search for teacher)
    workflow.add_edge("retrieve", "synthesize")
    workflow.add_edge("synthesize", "reasoning")
    workflow.add_edge("reasoning", "generate_teacher_outline")
    workflow.add_edge("generate_teacher_outline", "generate_teacher_script")
    workflow.add_edge("generate_teacher_script", "validate")

    # ── Validation loop (max 3 regenerations) ─────────────────────────────────
    workflow.add_conditional_edges(
        "validate",
        should_regenerate,
        {"regenerate": "regenerate", "segment_script": "fact_check"},
    )
    workflow.add_edge("regenerate", "validate")

    # ── Fact-check loop (max 2 iterations) ─────────────────────────────────────
    workflow.add_conditional_edges(
        "fact_check",
        should_pass_factcheck,
        {
            "segment_script": "segment_script",
            "regenerate_after_factcheck": "regenerate_after_factcheck",
        },
    )
    workflow.add_edge("regenerate_after_factcheck", "fact_check")

    # ── Post-segmentation pipeline ─────────────────────────────────────────────
    workflow.add_edge("segment_script", "generate_audio")
    workflow.add_edge("generate_audio", "extract_entities")
    workflow.add_edge("extract_entities", "generate_images")
    workflow.add_edge("generate_images", "generate_video")
    workflow.add_edge("generate_video", "save_execution_report")
    workflow.add_edge("save_execution_report", END)

    return workflow.compile()


# =============================================================================
# EXECUTION ENTRY POINT
# =============================================================================

async def execute_teacher_agent(state: AgentState) -> AgentState:
    """
    Execute the teacher graph with the given initial state.

    Args:
        state: Initial AgentState from create_teacher_initial_state()

    Returns:
        Final AgentState after execution.
    """
    graph = create_teacher_graph()

    try:
        final_state = await asyncio.to_thread(graph.invoke, state)
        return final_state
    except Exception as exc:
        state["error"] = f"Teacher graph execution failed: {str(exc)}"
        return state

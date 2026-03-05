"""
LangGraph State Machine for Agent Workflow.

This module implements the StateGraph that orchestrates the ReAct agent loop:

Graph Flow:
    START → retrieve → web_search → synthesize → generate_outline → generate_script
          → validate → [regenerate loop or END]

Nodes:
    - retrieve: Get best practices from Pinecone
    - web_search: Optional web search (if duration > 10 min)
    - synthesize: Combine context into insights
    - generate_outline: Create script structure
    - generate_script: Generate full script
    - validate: Check script length (90-110%)
    - regenerate: Retry with adjustments (if validation fails)

Edges:
    - Conditional: should_regenerate() → regenerate or END
    - Iteration limit: max 3 attempts
    - Token budget: max 35k tokens
"""

from typing import Dict, Any, Literal, Annotated, TypedDict
from datetime import datetime, timezone
import operator
import logging

# Initialize logger for graph execution
logger = logging.getLogger(__name__)

# Handle both module and standalone execution
try:
    from agent.config import MAX_ITERATIONS, MAX_TOTAL_TOKENS
    from agent.models import AgentState, ReasoningStep
    from agent.tools import (
        retrieve_tool,
        web_search_tool,
        synthesize_tool,
        generate_outline_tool,
        generate_script_tool,
        validate_tool,
        regenerate_tool,
        segment_script_tool,
        generate_tts_tool,
        create_project_directory,
        save_script_to_file,
        save_segments_to_file,
        create_project_slug,
    )
except ModuleNotFoundError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from agent.config import MAX_ITERATIONS, MAX_TOTAL_TOKENS
    from agent.models import AgentState, ReasoningStep
    from agent.tools import (
        retrieve_tool,
        web_search_tool,
        synthesize_tool,
        generate_outline_tool,
        generate_script_tool,
        validate_tool,
        regenerate_tool,
        segment_script_tool,
        generate_tts_tool,
        create_project_directory,
        save_script_to_file,
        save_segments_to_file,
        create_project_slug,
    )

from langgraph.graph import StateGraph, END


# =============================================================================
# STATE SCHEMA FOR LANGGRAPH
# =============================================================================

class GraphState(TypedDict):
    """
    State schema for LangGraph with explicit field definitions.
    Use dict-based state to avoid TypedDict compatibility issues with Python 3.14.
    """
    # Input fields
    request_id: str
    project_name: str
    project_slug: str  # URL-safe project name
    project_dir: str   # Path to project directory
    genre: str
    idea: str
    duration: int
    language: str
    target_chars: int
    
    # Context fields
    retrieved_context: str
    web_context: str
    synthesized_context: str
    retrieved_sources_count: int
    
    # ReAct reasoning fields (NEW)
    reasoning: str
    reasoning_strategy: dict
    
    # Output fields
    outline: str
    script: str
    char_count: int
    
    # Validation fields
    validation_passed: bool
    validation_ratio: float
    validation_message: str
    
    # Control fields
    iteration: int
    max_iterations: int
    web_search_enabled: bool
    should_regenerate: bool
    
    # Tracking fields (use operator.add for list accumulation)
    reasoning_trace: Annotated[list, operator.add]
    tokens_used: int
    
    # Segmentation and audio fields (NEW)
    segments: list
    segment_count: int
    audio_files: list
    audio_base_url: str
    audio_files_count: int
    
    # Error handling
    error: str


# =============================================================================
# NODE IMPLEMENTATIONS
# =============================================================================

def create_project_node(state: AgentState) -> AgentState:
    """
    Node: Create project directory structure at the start.
    
    Updates state:
        - project_slug
        - project_dir
        - reasoning_trace
    """
    print(f"  [GRAPH] Entering create_project_node...")
    
    result = create_project_directory(state['project_name'])
    
    if result['success']:
        print(f"  [GRAPH] Project directory created: {result['project_dir']}")
    else:
        print(f"  [GRAPH] WARNING: Failed to create project directory: {result['error']}")
    
    # Add reasoning trace
    trace_step = ReasoningStep(
        step=f"create_project (iteration {state['iteration']})",
        action="create_project_directory",
        observation=f"Directory: {result['project_dir']}" if result['success'] else f"Error: {result['error']}",
        thought=f"Created project directory for '{state['project_name']}'"
    )
    
    print(f"  [GRAPH] Exiting create_project_node (slug: '{result['project_slug']}')")
    print(f"  [GRAPH] Returning: project_slug={result['project_slug']}, project_dir={result['project_dir']}")
    logger.info(f"[GRAPH] create_project_node returning: project_slug='{result['project_slug']}', project_dir='{result['project_dir']}'")
    
    # MUST return ALL updates including project_slug and project_dir
    # These are regular fields (not operator.add) so they'll be merged normally
    return {
        "project_slug": result['project_slug'],
        "project_dir": result['project_dir'],
        "reasoning_trace": [trace_step]
    }


def retrieve_node(state: AgentState) -> AgentState:
    """
    Node: Retrieve storytelling best practices from Pinecone.
    
    Updates state:
        - retrieved_context
        - retrieved_sources_count
        - tokens_used
        - reasoning_trace
    """
    print(f"  [GRAPH] Entering retrieve_node...")
    query = f"{state['genre']} {state['idea']}"
    
    print(f"  [GRAPH] Calling retrieve_tool with query='{query[:50]}...'")
    result = retrieve_tool(
        query=query,
        language=state['language'],
        top_k=5
    )
    print(f"  [GRAPH] retrieve_tool returned: success={result['success']}, sources={result['sources_count']}")
    
    # Update state
    state['retrieved_context'] = result['context']
    state['retrieved_sources_count'] = result['sources_count']
    state['tokens_used'] += result['tokens_used']
    
    # Add reasoning step
    step = {
        "step": len(state['reasoning_trace']) + 1,
        "action": "retrieve_pinecone",
        "result": f"Retrieved {result['sources_count']} sources ({len(result['context'])} chars)" if result['success'] else f"Error: {result.get('error')}",
        "tokens_used": result['tokens_used'],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    state['reasoning_trace'].append(step)
    
    if result.get('error'):
        state['error'] = f"Retrieve failed: {result['error']}"
    
    print(f"  [GRAPH] Exiting retrieve_node")
    return state


def web_search_node(state: AgentState) -> AgentState:
    """
    Node: Optional web search for additional context.
    
    Only executes if:
        - duration > 10 minutes
        - SERPAPI_API_KEY is set
    
    Updates state:
        - web_context
        - tokens_used
        - reasoning_trace
    """
    print(f"  [GRAPH] Entering web_search_node... (duration={state['duration']} min)")
    result = web_search_tool(
        query=f"{state['genre']} storytelling techniques",
        duration=state['duration'],
        language=state['language']
    )
    print(f"  [GRAPH] web_search_tool returned: skipped={result.get('skipped', False)}")
    
    # Update state
    state['web_context'] = result['context']
    
    # Add reasoning step
    action_desc = "web_search (skipped)" if result.get('skipped') else "web_search"
    result_desc = result.get('error') if result.get('error') else \
                  f"Skipped ({result.get('error', 'duration <= 10 min or no API key')})" if result.get('skipped') else \
                  f"Found {result['sources_count']} results"
    
    step = {
        "step": len(state['reasoning_trace']) + 1,
        "action": action_desc,
        "result": result_desc,
        "tokens_used": 0,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    state['reasoning_trace'].append(step)
    
    print(f"  [GRAPH] Exiting web_search_node")
    return state


def synthesize_node(state: AgentState) -> AgentState:
    """
    Node: Synthesize retrieved + web context into unified insights.
    
    Updates state:
        - synthesized_context
        - tokens_used
        - reasoning_trace
    """
    print(f"  [GRAPH] Entering synthesize_node...")
    result = synthesize_tool(
        retrieved_context=state['retrieved_context'],
        web_context=state['web_context'],
        genre=state['genre'],
        idea=state['idea'],
        language=state['language']
    )
    
    # Update state
    state['synthesized_context'] = result.get('synthesized_context', '')
    state['tokens_used'] += result.get('tokens_used', 0)
    
    # Add reasoning step
    step = {
        "step": len(state['reasoning_trace']) + 1,
        "action": "synthesize_context",
        "result": f"Generated {len(result.get('synthesized_context', ''))} chars of insights" if result['success'] else f"Error: {result.get('error')}",
        "tokens_used": result.get('tokens_used', 0),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    state['reasoning_trace'].append(step)
    
    if result.get('error'):
        state['error'] = f"Synthesis failed: {result['error']}"
    
    print(f"  [GRAPH] Exiting synthesize_node")
    return state


def reasoning_node(state: AgentState) -> AgentState:
    """
    Node: ReAct reasoning - analyze context and decide creative strategy.
    
    Updates state:
        - reasoning
        - reasoning_strategy
        - tokens_used
        - reasoning_trace
    """
    print(f"  [GRAPH] Entering reasoning_node (ReAct thinking)...")
    from agent.tools import reasoning_tool
    
    result = reasoning_tool(
        genre=state['genre'],
        idea=state['idea'],
        duration=state['duration'],
        synthesized_context=state['synthesized_context'],
        language=state['language']
    )
    
    # Update state
    state['reasoning'] = result.get('reasoning', '')
    state['reasoning_strategy'] = result.get('strategy', {})
    state['tokens_used'] += result.get('tokens_used', 0)
    
    # Add reasoning step
    step = {
        "step": len(state['reasoning_trace']) + 1,
        "action": "react_reasoning",
        "result": f"Strategy: {result.get('strategy', {})} ({len(result.get('reasoning', ''))} chars reasoning)" if result['success'] else f"Error: {result.get('error')}",
        "tokens_used": result.get('tokens_used', 0),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    state['reasoning_trace'].append(step)
    
    if result.get('error'):
        state['error'] = f"Reasoning failed: {result['error']}"
    
    print(f"  [GRAPH] Exiting reasoning_node (strategy: {state['reasoning_strategy'].get('tone', 'N/A')})")
    return state


def generate_outline_node(state: AgentState) -> AgentState:
    """
    Node: Generate script outline using synthesized context.
    
    Updates state:
        - outline
        - tokens_used
        - reasoning_trace
    """
    print(f"  [GRAPH] Entering generate_outline_node...")
    result = generate_outline_tool(
        genre=state['genre'],
        idea=state['idea'],
        duration=state['duration'],
        synthesized_context=state['synthesized_context'],
        language=state['language'],
        target_chars=state['target_chars'],
        reasoning_strategy=state.get('reasoning', '')  # Pass reasoning to guide outline
    )
    
    # Update state
    state['outline'] = result.get('outline', '')
    state['tokens_used'] += result.get('tokens_used', 0)
    
    # Add reasoning step
    step = {
        "step": len(state['reasoning_trace']) + 1,
        "action": "generate_outline",
        "result": f"Generated outline ({len(result['outline'])} chars)" if result['success'] else f"Error: {result.get('error')}",
        "tokens_used": result['tokens_used'],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    state['reasoning_trace'].append(step)
    
    if result.get('error'):
        state['error'] = f"Outline generation failed: {result['error']}"
    
    print(f"  [GRAPH] Exiting generate_outline_node")
    return state


def generate_script_node(state: AgentState) -> AgentState:
    """
    Node: Generate full script from outline.
    
    Updates state:
        - script
        - char_count
        - tokens_used
        - reasoning_trace
    """
    print(f"  [GRAPH] Entering generate_script_node (iteration {state['iteration']})...")
    result = generate_script_tool(
        outline=state['outline'],
        genre=state['genre'],
        idea=state['idea'],
        duration=state['duration'],
        language=state['language'],
        target_chars=state['target_chars'],
        iteration=state['iteration']
    )
    
    # Update state
    state['script'] = result.get('script', '')
    state['char_count'] = result.get('char_count', 0)
    state['tokens_used'] += result.get('tokens_used', 0)
    
    # Add reasoning step
    step = {
        "step": len(state['reasoning_trace']) + 1,
        "action": f"generate_script (iteration {state['iteration'] + 1})",
        "result": f"Generated {result.get('char_count', 0):,} chars" if result['success'] else f"Error: {result.get('error')}",
        "tokens_used": result.get('tokens_used', 0),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    state['reasoning_trace'].append(step)
    
    if result.get('error'):
        state['error'] = f"Script generation failed: {result['error']}"
    
    print(f"  [GRAPH] Exiting generate_script_node (generated {result.get('char_count', 0)} chars)")
    return state


def validate_node(state: AgentState) -> AgentState:
    """
    Node: Validate script length (90-110% of target).
    
    Updates state:
        - validation_passed
        - validation_ratio
        - validation_message
        - reasoning_trace
    """
    logger.info(f"[GRAPH] Entering validate_node (project_slug: '{state.get('project_slug', 'NOT SET')}')")
    print(f"  [GRAPH] Entering validate_node (project_slug: '{state.get('project_slug', 'NOT SET')}')")
    
    result = validate_tool(
        script=state['script'],
        target_chars=state['target_chars']
    )
    
    # Update state
    state['validation_passed'] = result['is_valid']
    state['validation_ratio'] = result['ratio']
    state['validation_message'] = result['message']
    
    # Save script to file if validation passes
    project_slug = state.get('project_slug')
    logger.info(f"[GRAPH] Validation result: is_valid={result['is_valid']}, project_slug='{project_slug}'")
    print(f"  [GRAPH] Validation result: is_valid={result['is_valid']}, project_slug='{project_slug}'")
    
    if result['is_valid'] and project_slug:
        logger.info(f"[GRAPH] Validation passed, saving script to file...")
        print(f"  [GRAPH] Validation passed, saving script to file...")
        save_result = save_script_to_file(state['script'], project_slug)
        if save_result['success']:
            logger.info(f"[GRAPH] ✓ Script saved: {save_result['file_path']}")
            print(f"  [GRAPH] ✓ Script saved: {save_result['file_path']}")
        else:
            logger.error(f"[GRAPH] ✗ WARNING: Failed to save script: {save_result['error']}")
            print(f"  [GRAPH] ✗ WARNING: Failed to save script: {save_result['error']}")
    else:
        if not result['is_valid']:
            logger.info(f"[GRAPH] Validation failed, skipping script save")
            print(f"  [GRAPH] Validation failed, skipping script save")
        if not project_slug:
            logger.error(f"[GRAPH] ✗ ERROR: project_slug is empty, cannot save script!")
            print(f"  [GRAPH] ✗ ERROR: project_slug is empty, cannot save script!")
    
    # Add reasoning step
    step = {
        "step": len(state['reasoning_trace']) + 1,
        "action": "validate_length",
        "result": result['message'],
        "tokens_used": 0,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    state['reasoning_trace'].append(step)
    
    return state


def regenerate_node(state: AgentState) -> AgentState:
    """
    Node: Regenerate script with length adjustment instructions.
    
    Increments iteration counter.
    
    Updates state:
        - script
        - char_count
        - iteration
        - tokens_used
        - reasoning_trace
    """
    # Increment iteration
    state['iteration'] += 1
    
    result = regenerate_tool(
        outline=state['outline'],
        genre=state['genre'],
        idea=state['idea'],
        duration=state['duration'],
        language=state['language'],
        target_chars=state['target_chars'],
        actual_chars=state['char_count'],
        iteration=state['iteration']
    )
    
    # Update state
    state['script'] = result.get('script', '')
    state['char_count'] = result.get('char_count', 0)
    state['tokens_used'] += result.get('tokens_used', 0)
    
    # Add reasoning step
    step = {
        "step": len(state['reasoning_trace']) + 1,
        "action": f"regenerate_script (iteration {state['iteration'] + 1})",
        "result": f"Regenerated: {result.get('char_count', 0):,} chars" if result['success'] else f"Error: {result.get('error')}",
        "tokens_used": result.get('tokens_used', 0),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    state['reasoning_trace'].append(step)
    
    if result.get('error'):
        state['error'] = f"Regeneration failed: {result['error']}"
    
    return state


def segment_script_node(state: AgentState) -> AgentState:
    """
    Node: Segment script into visual moments (2-6 sentences each).
    
    Updates state:
        - segments
        - segment_count
        - tokens_used (incremental)
        - reasoning_trace
    """
    print(f"  [GRAPH] Entering segment_script_node (project_slug: '{state.get('project_slug', 'NOT SET')}')")
    
    result = segment_script_tool(
        script=state['script'],
        language=state['language']
    )
    
    # Update state
    if result['success']:
        state['segments'] = result['segments']
        state['segment_count'] = result['segment_count']
        state['tokens_used'] += result.get('tokens_used', 0)
        
        # Save segments to file
        project_slug = state.get('project_slug')
        script = state.get('script')
        print(f"  [GRAPH] Segmentation result: success=True, segments={len(result['segments'])}, project_slug='{project_slug}'")
        
        if project_slug and script:
            print(f"  [GRAPH] Segmentation successful, saving segments to file...")
            save_result = save_segments_to_file(
                segments=result['segments'],
                script=script,
                project_slug=project_slug
            )
            if save_result['success']:
                print(f"  [GRAPH] ✓ Segments saved: {save_result['file_path']}")
            else:
                print(f"  [GRAPH] ✗ WARNING: Failed to save segments: {save_result['error']}")
        else:
            if not project_slug:
                print(f"  [GRAPH] ✗ ERROR: project_slug is empty, cannot save segments!")
            if not script:
                print(f"  [GRAPH] ✗ ERROR: script is empty, cannot save segments!")
    else:
        # Fallback was used or failed completely
        state['error'] = f"Segmentation failed: {result.get('error', 'Unknown error')}"
    
    # Add reasoning step
    step = {
        "step": len(state['reasoning_trace']) + 1,
        "action": "segment_script",
        "result": f"Created {result.get('segment_count', 0)} segments" + (f" (fallback used)" if result.get('error') else ""),
        "tokens_used": result.get('tokens_used', 0),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    state['reasoning_trace'].append(step)
    
    return state


def generate_audio_node(state: AgentState) -> AgentState:
    """
    Node: Generate TTS audio files for each segment.
    
    Updates state:
        - segments (with audio_url field)
        - audio_files
        - audio_files_count
        - reasoning_trace
    """
    result = generate_tts_tool(
        segments=state['segments'],
        project_name=state['project_name'],
        audio_base_url=state['audio_base_url'],
        voice="alloy"
    )
    
    # Update state
    if result['success']:
        state['segments'] = result['segments']  # Now with audio_url fields
        state['audio_files'] = result['audio_files']
        state['audio_files_count'] = result['audio_files_count']
    else:
        # Partial or complete failure
        state['error'] = f"Audio generation failed: {result.get('error', 'Unknown error')}"
    
    # Add reasoning step
    step = {
        "step": len(state['reasoning_trace']) + 1,
        "action": "generate_audio",
        "result": f"Generated {result.get('audio_files_count', 0)} audio files",
        "tokens_used": 0,  # TTS doesn't use tokens
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    state['reasoning_trace'].append(step)
    
    return state


# =============================================================================
# CONDITIONAL EDGES
# =============================================================================

def should_regenerate(state: AgentState) -> Literal["regenerate", "segment_script"]:
    """
    Conditional edge: Decide whether to regenerate or proceed to segmentation.
    
    Regenerate if:
        - Validation failed
        - Iteration < MAX_ITERATIONS
        - Tokens < MAX_TOTAL_TOKENS
        - No errors
    
    Otherwise proceed to segment_script.
    """
    # Check if validation passed
    if state.get('validation_passed'):
        return "segment_script"
    
    # Check if error occurred
    if state.get('error'):
        return "segment_script"  # Still segment even if there's an error
    
    # Check iteration limit
    if state['iteration'] >= state['max_iterations']:
        return "segment_script"  # Still segment even if iterations exceeded
    
    # Check token budget
    if state['tokens_used'] >= MAX_TOTAL_TOKENS:
        state['error'] = f"Token budget exceeded: {state['tokens_used']}/{MAX_TOTAL_TOKENS}"
        return "segment_script"  # Still segment even if budget exceeded
    
    return "regenerate"


# =============================================================================
# GRAPH DEFINITION
# =============================================================================

def create_agent_graph():
    """
    Create and compile the LangGraph StateGraph.
    
    Returns:
        Compiled graph ready for execution
    """
    # Initialize graph with GraphState schema
    workflow = StateGraph(GraphState)
    
    # Add nodes
    workflow.add_node("create_project", create_project_node)  # NEW: Create project directory (first!)
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("synthesize", synthesize_node)
    workflow.add_node("reasoning", reasoning_node)  # NEW: ReAct reasoning
    workflow.add_node("generate_outline", generate_outline_node)
    workflow.add_node("generate_script", generate_script_node)
    workflow.add_node("validate", validate_node)
    workflow.add_node("regenerate", regenerate_node)
    workflow.add_node("segment_script", segment_script_node)  # NEW: Script segmentation
    workflow.add_node("generate_audio", generate_audio_node)  # NEW: Audio generation
    
    # Set entry point (create project directory first!)
    workflow.set_entry_point("create_project")
    
    # Add sequential edges (main flow)
    workflow.add_edge("create_project", "retrieve")  # NEW: create_project -> retrieve
    workflow.add_edge("retrieve", "web_search")
    workflow.add_edge("web_search", "synthesize")
    workflow.add_edge("synthesize", "reasoning")  # NEW: reasoning after synthesis
    workflow.add_edge("reasoning", "generate_outline")  # reasoning before outline
    workflow.add_edge("generate_outline", "generate_script")
    workflow.add_edge("generate_script", "validate")
    
    # Add conditional edge (validation → regenerate or segment_script)
    workflow.add_conditional_edges(
        "validate",
        should_regenerate,
        {
            "regenerate": "regenerate",
            "segment_script": "segment_script"
        }
    )
    
    # Regenerate loops back to validate
    workflow.add_edge("regenerate", "validate")
    
    # NEW: Segmentation and audio pipeline
    workflow.add_edge("segment_script", "generate_audio")
    workflow.add_edge("generate_audio", END)
    
    # Compile graph
    return workflow.compile()


# =============================================================================
# GRAPH EXECUTION
# =============================================================================

async def execute_agent(state: AgentState) -> AgentState:
    """
    Execute the agent graph with the given initial state.
    
    Args:
        state: Initial AgentState from request
        
    Returns:
        Final AgentState after execution
    """
    import asyncio
    
    graph = create_agent_graph()
    
    # Execute graph in thread pool to avoid blocking event loop
    try:
        # Run synchronous invoke in executor thread
        final_state = await asyncio.to_thread(graph.invoke, state)
        return final_state
    except Exception as e:
        state['error'] = f"Graph execution failed: {str(e)}"
        return state


# =============================================================================
# CLI FOR TESTING
# =============================================================================

if __name__ == "__main__":
    """Test graph structure and execution flow."""
    print("=" * 80)
    print("LANGGRAPH STATE MACHINE TEST")
    print("=" * 80)
    
    # Test 1: Graph structure
    print("\n1. Testing graph structure:")
    print("-" * 80)
    
    try:
        graph = create_agent_graph()
        print("  ✓ Graph compiled successfully")
        
        # Get graph representation
        nodes = ["retrieve", "web_search", "synthesize", "generate_outline", 
                 "generate_script", "validate", "regenerate"]
        print(f"  ✓ Nodes: {len(nodes)}")
        for i, node in enumerate(nodes, 1):
            print(f"    {i}. {node}")
        
        print("\n  ✓ Edges:")
        print("    - retrieve → web_search")
        print("    - web_search → synthesize")
        print("    - synthesize → generate_outline")
        print("    - generate_outline → generate_script")
        print("    - generate_script → validate")
        print("    - validate → [regenerate OR END] (conditional)")
        print("    - regenerate → validate (loop)")
        
    except Exception as e:
        print(f"  ✗ Graph creation failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Mock execution (dry run with minimal state)
    print("\n2. Testing mock execution:")
    print("-" * 80)
    
    from agent.models import create_initial_state, ScriptRequestItem
    
    # Create mock request
    mock_request = ScriptRequestItem(
        isValid=True,
        projectName="Test Project",
        genre="Comedy",
        storyIdea="A programmer creates an AI",
        duration=5,
        request_id="test-graph-123"
    )
    
    # Create initial state
    initial_state = create_initial_state(mock_request)
    
    print(f"  ✓ Initial state created:")
    print(f"    - Request ID: {initial_state['request_id']}")
    print(f"    - Language: {initial_state['language']}")
    print(f"    - Target chars: {initial_state['target_chars']:,}")
    print(f"    - Max iterations: {initial_state['max_iterations']}")
    print(f"    - Web search: {initial_state['web_search_enabled']}")
    
    # Test 3: Conditional edge logic
    print("\n3. Testing conditional edge logic:")
    print("-" * 80)
    
    test_cases = [
        ({
            'validation_passed': True,
            'iteration': 0,
            'max_iterations': 3,
            'tokens_used': 1000,
            'error': None
        }, "end", "validation passed"),
        ({
            'validation_passed': False,
            'iteration': 2,
            'max_iterations': 3,
            'tokens_used': 1000,
            'error': None
        }, "regenerate", "validation failed, under limits"),
        ({
            'validation_passed': False,
            'iteration': 3,
            'max_iterations': 3,
            'tokens_used': 1000,
            'error': None
        }, "end", "max iterations reached"),
        ({
            'validation_passed': False,
            'iteration': 0,
            'max_iterations': 3,
            'tokens_used': 1000,
            'error': "API error"
        }, "end", "error occurred"),
    ]
    
    for i, (test_state, expected, description) in enumerate(test_cases, 1):
        result = should_regenerate(test_state)  # type: ignore
        status = "✓" if result == expected else "✗"
        print(f"  {status} Test {i}: {description}")
        print(f"      Expected: {expected}, Got: {result}")
    
    # Test 4: Node function signatures
    print("\n4. Testing node function signatures:")
    print("-" * 80)
    
    node_functions = [
        retrieve_node,
        web_search_node,
        synthesize_node,
        generate_outline_node,
        generate_script_node,
        validate_node,
        regenerate_node
    ]
    
    for node_func in node_functions:
        try:
            # Check if function accepts AgentState and returns AgentState
            import inspect
            sig = inspect.signature(node_func)
            params = list(sig.parameters.keys())
            
            if len(params) == 1 and params[0] == 'state':
                print(f"  ✓ {node_func.__name__}: signature correct")
            else:
                print(f"  ✗ {node_func.__name__}: unexpected signature {params}")
        except Exception as e:
            print(f"  ✗ {node_func.__name__}: signature check failed - {e}")
    
    print("\n" + "=" * 80)
    print("✓ LANGGRAPH STATE MACHINE TEST COMPLETE")
    print("=" * 80)
    print("\nNote: Full execution test requires API keys and can be run via FastAPI")

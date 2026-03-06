"""
Agent Tools for ReAct Loop.

This module implements 8 tools that the agent can use:
1. retrieve_tool - Pinecone vector search with Cohere embeddings
2. web_search_tool - SerpAPI search (optional, for long videos >10 min)
3. synthesize_tool - Combine retrieved + web context
3.5. reasoning_tool - ReAct reasoning to plan creative strategy (NEW)
4. generate_outline_tool - Create script outline (max 2000 tokens)
5. generate_script_tool - Generate full script from outline
6. validate_tool - Check script length (90-110% of target)
7. regenerate_tool - Retry with adjustment instructions

Each tool returns structured output for the agent state.
"""

import os
import json
import re
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def create_project_slug(project_name: str) -> str:
    """Convert project name to URL-safe slug.
    
    Examples:
        "Horror Test" -> "Horror_Test"
        "My Amazing Project" -> "My_Amazing_Project"
    """
    # Replace spaces with underscores
    slug = project_name.replace(" ", "_")
    # Remove any characters that aren't alphanumeric, underscore, or hyphen
    slug = re.sub(r'[^\w\-]', '', slug)
    return slug


def create_project_directory(project_name: str) -> Dict[str, Any]:
    """Create project directory structure at the start of pipeline.
    
    Creates: projects/{project_slug}/
    
    Args:
        project_name: Original project name
        
    Returns:
        {
            "success": bool,
            "project_dir": str,  # Path to project directory
            "project_slug": str,
            "error": Optional[str]
        }
    """
    try:
        project_slug = create_project_slug(project_name)
        project_dir = Path("projects") / project_slug
        
        # Create directory
        project_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Created project directory: {project_dir}")
        
        return {
            "success": True,
            "project_dir": str(project_dir),
            "project_slug": project_slug,
            "error": None
        }
        
    except Exception as e:
        error_msg = f"Failed to create project directory: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "project_dir": "",
            "project_slug": "",
            "error": error_msg
        }


def save_script_to_file(script: str, project_slug: str) -> Dict[str, Any]:
    """Save validated script to text file.
    
    Creates: projects/{project_slug}/script.txt
    
    Args:
        script: Generated and validated script text
        project_slug: URL-safe project slug
        
    Returns:
        {
            "success": bool,
            "file_path": str,
            "error": Optional[str]
        }
    """
    try:
        project_dir = Path("projects") / project_slug
        project_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = project_dir / "script.txt"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("ORIGINAL SCRIPT\n")
            f.write("=" * 80 + "\n\n")
            f.write(script)
            f.write("\n\n")
            f.write("=" * 80 + "\n")
            f.write(f"Generated: {datetime.now(timezone.utc).isoformat()}\n")
            f.write(f"Length: {len(script)} characters\n")
        
        logger.info(f"Saved script to: {file_path} ({len(script)} chars)")
        
        return {
            "success": True,
            "file_path": str(file_path),
            "error": None
        }
        
    except Exception as e:
        error_msg = f"Failed to save script: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "file_path": "",
            "error": error_msg
        }


def save_segments_to_file(segments: List[Dict], script: str, project_slug: str) -> Dict[str, Any]:
    """Save segmented script to text file.
    
    Creates: projects/{project_slug}/script_segmented.txt
    
    Args:
        segments: List of segment dicts with segment_index, text, audio_url
        script: Original full script for comparison
        project_slug: URL-safe project slug
        
    Returns:
        {
            "success": bool,
            "file_path": str,
            "error": Optional[str]
        }
    """
    try:
        project_dir = Path("projects") / project_slug
        project_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = project_dir / "script_segmented.txt"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("SEGMENTED SCRIPT\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Total segments: {len(segments)}\n")
            f.write(f"Generated: {datetime.now(timezone.utc).isoformat()}\n\n")
            
            f.write("=" * 80 + "\n")
            f.write("FULL SCRIPT (ORIGINAL)\n")
            f.write("=" * 80 + "\n\n")
            f.write(script)
            f.write("\n\n")
            
            f.write("=" * 80 + "\n")
            f.write(f"SEGMENTS ({len(segments)} total)\n")
            f.write("=" * 80 + "\n\n")
            
            for seg in segments:
                segment_index = seg.get('segment_index', 0)
                text = seg.get('text', '')
                audio_url = seg.get('audio_url', 'N/A')
                
                f.write(f"[Segment {segment_index}]\n")
                f.write("-" * 80 + "\n")
                f.write(f"{text}\n\n")
                f.write(f"Audio URL: {audio_url}\n")
                f.write(f"Character count: {len(text)}\n")
                f.write("\n" + "=" * 80 + "\n\n")
        
        logger.info(f"Saved segmented script to: {file_path} ({len(segments)} segments)")
        
        return {
            "success": True,
            "file_path": str(file_path),
            "error": None
        }
        
    except Exception as e:
        error_msg = f"Failed to save segments: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "file_path": "",
            "error": error_msg
        }


def save_execution_report(state: Dict[str, Any]) -> Dict[str, Any]:
    """Save detailed execution report to project directory.
    
    Creates: projects/{project_slug}/execution_report.txt
    
    This report contains comprehensive information about the entire execution:
    - Full reasoning trace with timestamps
    - Token usage breakdown by step
    - Pinecone retrieval statistics
    - Error log (if any)
    - Retry attempts
    - Script validation results
    - Segmentation and audio generation stats
    - Performance metrics
    
    Args:
        state: Complete AgentState after workflow execution
        
    Returns:
        {
            "success": bool,
            "file_path": str,
            "error": Optional[str]
        }
    """
    try:
        project_slug = state.get('project_slug', 'unknown_project')
        project_dir = Path("projects") / project_slug
        project_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = project_dir / "execution_report.txt"
        
        # Extract data from state
        request_id = state.get('request_id', 'N/A')
        project_name = state.get('project_name', 'N/A')
        genre = state.get('genre', 'N/A')
        duration = state.get('duration', 0)
        language = state.get('language', 'N/A')
        target_chars = state.get('target_chars', 0)
        
        reasoning_trace = state.get('reasoning_trace', [])
        total_tokens = state.get('tokens_used', 0)
        
        retrieved_sources_count = state.get('retrieved_sources_count', 0)
        web_search_enabled = state.get('web_search_enabled', False)
        
        iteration = state.get('iteration', 0)
        max_iterations = state.get('max_iterations', 3)
        validation_passed = state.get('validation_passed', False)
        validation_ratio = state.get('validation_ratio', 0.0)
        validation_message = state.get('validation_message', 'N/A')
        
        char_count = state.get('char_count', 0)
        segment_count = state.get('segment_count', 0)
        audio_files_count = state.get('audio_files_count', 0)
        tts_characters = state.get('tts_characters', 0)
        tts_estimated_cost = state.get('tts_estimated_cost', 0.0)
        
        error = state.get('error', None)
        
        # Calculate metrics
        total_steps = len(reasoning_trace)
        regeneration_count = iteration - 1 if iteration > 1 else 0
        
        # Check if there were any retries (by looking for retry indicators in errors)
        retry_count = 0
        error_log = []
        if error:
            error_log.append(error)
        
        # Analyze reasoning trace for retries and errors
        for step in reasoning_trace:
            step_result = step.get('result', '')
            if 'retry' in step_result.lower() or 'attempt' in step_result.lower():
                retry_count += 1
            if 'error' in step_result.lower() or 'failed' in step_result.lower():
                error_log.append(f"Step {step.get('step')}: {step_result}")
        
        # Calculate expected vs actual duration
        actual_duration_estimate = char_count / target_chars * duration if target_chars > 0 else 0
        duration_match = abs(actual_duration_estimate - duration) <= 1.0  # Within 1 minute
        
        # Token breakdown by action
        token_breakdown = {}
        for step in reasoning_trace:
            action = step.get('action', 'unknown')
            tokens = step.get('tokens_used', 0)
            if action not in token_breakdown:
                token_breakdown[action] = 0
            token_breakdown[action] += tokens
        
        # Write report
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("PROJECT EXECUTION REPORT\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Generated: {datetime.now(timezone.utc).isoformat()}\n")
            f.write(f"Request ID: {request_id}\n")
            f.write("\n")
            
            # === PROJECT INFORMATION ===
            f.write("=" * 80 + "\n")
            f.write("PROJECT INFORMATION\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Project Name: {project_name}\n")
            f.write(f"Project Slug: {project_slug}\n")
            f.write(f"Genre: {genre}\n")
            f.write(f"Language: {language}\n")
            f.write(f"Target Duration: {duration} minutes\n")
            f.write(f"Target Characters: {target_chars:,}\n")
            f.write("\n")
            
            # === EXECUTION SUMMARY ===
            f.write("=" * 80 + "\n")
            f.write("EXECUTION SUMMARY\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Total Steps: {total_steps}\n")
            f.write(f"Total Iterations: {iteration}\n")
            f.write(f"Regeneration Count: {regeneration_count}\n")
            f.write(f"Retry Attempts: {retry_count}\n")
            f.write(f"Status: {'✓ SUCCESS' if not error else '✗ ERROR'}\n")
            f.write("\n")
            
            # === RESOURCE USAGE ===
            f.write("=" * 80 + "\n")
            f.write("RESOURCE USAGE\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Total Tokens Used: {total_tokens:,}\n")
            f.write(f"Pinecone Queries: {retrieved_sources_count}\n")
            f.write(f"Web Search Enabled: {'Yes' if web_search_enabled else 'No'}\n")
            f.write("\n")
            
            f.write("Token Breakdown by Action:\n")
            for action, tokens in sorted(token_breakdown.items(), key=lambda x: x[1], reverse=True):
                f.write(f"  - {action}: {tokens:,} tokens\n")
            f.write("\n")
            
            # TTS cost (character-based pricing, not token-based)
            if tts_characters > 0:
                f.write("TTS API Usage (Character-Based Pricing):\n")
                f.write(f"  - Characters Processed: {tts_characters:,}\n")
                f.write(f"  - Estimated Cost: ${tts_estimated_cost:.4f} (at $0.015/1K chars)\n")
                f.write("\n")
            
            # === SCRIPT VALIDATION ===
            f.write("=" * 80 + "\n")
            f.write("SCRIPT VALIDATION\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Validation Status: {'✓ PASSED' if validation_passed else '✗ FAILED'}\n")
            f.write(f"Script Length: {char_count:,} characters\n")
            f.write(f"Target Length: {target_chars:,} characters\n")
            f.write(f"Length Ratio: {validation_ratio:.1%}\n")
            f.write(f"Validation Message: {validation_message}\n")
            f.write("\n")
            
            f.write(f"Estimated Duration: {actual_duration_estimate:.1f} minutes\n")
            f.write(f"Target Duration: {duration} minutes\n")
            f.write(f"Duration Match: {'✓ YES' if duration_match else '✗ NO'}\n")
            f.write("\n")
            
            # === SEGMENTATION & AUDIO ===
            f.write("=" * 80 + "\n")
            f.write("SEGMENTATION & AUDIO GENERATION\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Script Segments Created: {segment_count}\n")
            f.write(f"Audio Files Generated: {audio_files_count}\n")
            f.write(f"TTS Characters Processed: {tts_characters:,}\n")
            f.write(f"TTS Estimated Cost: ${tts_estimated_cost:.4f}\n")
            f.write(f"Segmentation Success: {'✓ YES' if segment_count > 0 else '✗ NO'}\n")
            f.write(f"Audio Generation Success: {'✓ YES' if audio_files_count > 0 else '✗ NO'}\n")
            f.write("\n")
            
            # === ERROR LOG ===
            if error_log:
                f.write("=" * 80 + "\n")
                f.write("ERROR LOG\n")
                f.write("=" * 80 + "\n\n")
                
                for i, err in enumerate(error_log, 1):
                    f.write(f"{i}. {err}\n")
                f.write("\n")
            
            # === FULL REASONING TRACE ===
            f.write("=" * 80 + "\n")
            f.write("FULL REASONING TRACE\n")
            f.write("=" * 80 + "\n\n")
            
            if reasoning_trace:
                for step in reasoning_trace:
                    step_num = step.get('step', 0)
                    action = step.get('action', 'unknown')
                    result = step.get('result', 'N/A')
                    tokens = step.get('tokens_used', 0)
                    timestamp = step.get('timestamp', 'N/A')
                    
                    f.write(f"[Step {step_num}] {action}\n")
                    f.write(f"  Timestamp: {timestamp}\n")
                    f.write(f"  Result: {result}\n")
                    f.write(f"  Tokens Used: {tokens:,}\n")
                    f.write("\n")
            else:
                f.write("No reasoning trace available.\n\n")
            
            # === PERFORMANCE METRICS ===
            f.write("=" * 80 + "\n")
            f.write("PERFORMANCE METRICS\n")
            f.write("=" * 80 + "\n\n")
            
            if reasoning_trace and len(reasoning_trace) > 1:
                # Calculate execution time (first to last timestamp)
                try:
                    first_time = datetime.fromisoformat(reasoning_trace[0].get('timestamp', ''))
                    last_time = datetime.fromisoformat(reasoning_trace[-1].get('timestamp', ''))
                    execution_time = (last_time - first_time).total_seconds()
                    
                    f.write(f"Total Execution Time: {execution_time:.1f} seconds ({execution_time/60:.1f} minutes)\n")
                    f.write(f"Average Time per Step: {execution_time/total_steps:.1f} seconds\n")
                    f.write(f"Tokens per Second: {total_tokens/execution_time:.1f}\n")
                except:
                    f.write("Execution time calculation unavailable.\n")
            else:
                f.write("Insufficient data for performance metrics.\n")
            
            f.write("\n")
            f.write("=" * 80 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 80 + "\n")
        
        logger.info(f"Saved execution report to: {file_path}")
        
        return {
            "success": True,
            "file_path": str(file_path),
            "error": None
        }
        
    except Exception as e:
        error_msg = f"Failed to save execution report: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "file_path": "",
            "error": error_msg
        }


# Handle both module and standalone execution
try:
    from agent.config import (
        OPENAI_MODEL,
        MAX_OUTLINE_TOKENS,
        PINECONE_INDEX_NAME,
        WEB_SEARCH_DURATION_THRESHOLD,
        OUTLINE_TEMPERATURE,
        SCRIPT_TEMPERATURE,
        MAX_SCRIPT_TOKENS_BASE,
    )
    from agent.language_utils import (
        validate_script_length,
        get_length_adjustment_instruction,
    )
except ModuleNotFoundError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from agent.config import (
        OPENAI_MODEL,
        MAX_OUTLINE_TOKENS,
        PINECONE_INDEX_NAME,
        WEB_SEARCH_DURATION_THRESHOLD,
        OUTLINE_TEMPERATURE,
        SCRIPT_TEMPERATURE,
        MAX_SCRIPT_TOKENS_BASE,
    )
    from agent.language_utils import (
        validate_script_length,
        get_length_adjustment_instruction,
    )

# Lazy imports for external libraries
from tenacity import retry, stop_after_attempt, wait_exponential
from functools import lru_cache


# =============================================================================
# GLOBAL LLM FACTORY (REUSABLE CLIENT)
# =============================================================================

@lru_cache(maxsize=4)
def get_llm(temperature: float, max_tokens: Optional[int] = None):
    """
    Get or create a cached ChatOpenAI instance.
    
    Uses LRU cache to reuse clients with same parameters.
    Supports up to 4 different configurations (synthesize, reasoning, outline, script).
    
    Args:
        temperature: Model temperature (0.0-1.0)
        max_tokens: Maximum tokens to generate (optional)
        
    Returns:
        ChatOpenAI instance
    """
    from langchain_openai import ChatOpenAI
    
    kwargs = {
        "model": OPENAI_MODEL,
        "temperature": temperature,
        "api_key": os.getenv("OPENAI_API_KEY"),
        "streaming": False,  # Disable streaming for API optimization
    }
    
    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens
    
    return ChatOpenAI(**kwargs)


def calculate_max_script_tokens(target_chars: int) -> int:
    """
    Calculate dynamic max_tokens limit for script generation.
    
    Uses 4:1 char-to-token ratio with 20% buffer.
    
    Args:
        target_chars: Target character count
        
    Returns:
        Max tokens limit
    """
    # Rough estimate: 4 chars = 1 token
    estimated_tokens = target_chars // 4
    
    # Add 20% buffer for flexibility
    max_tokens = int(estimated_tokens * 1.2)
    
    # Ensure minimum and maximum bounds
    max_tokens = max(2000, min(max_tokens, MAX_SCRIPT_TOKENS_BASE))
    
    return max_tokens


# =============================================================================
# TOOL 1: RETRIEVE FROM PINECONE
# =============================================================================

@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
def retrieve_tool(
    query: str,
    language: str,
    top_k: int = 5
) -> Dict[str, Any]:
    """
    Retrieve relevant storytelling best practices from Pinecone.
    
    Args:
        query: Search query (genre + story idea)
        language: Detected language ("ru" or "en")
        top_k: Number of results to retrieve
        
    Returns:
        {
            "success": bool,
            "context": str,  # Combined text from all chunks
            "sources_count": int,
            "tokens_used": int,  # Estimated
            "error": Optional[str]
        }
    """
    try:
        # Import Pinecone and Cohere
        from pinecone import Pinecone
        import cohere
        
        # Initialize clients
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        co = cohere.ClientV2(api_key=os.getenv("COHERE_API_KEY"))
        
        # Get index
        index = pc.Index(PINECONE_INDEX_NAME)
        
        # Generate query embedding using Cohere
        embed_response = co.embed(
            texts=[query],
            model="embed-english-v3.0",
            input_type="search_query",
            embedding_types=["float"]
        )
        query_embedding = embed_response.embeddings.float_[0]
        
        # Query Pinecone
        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        # Extract text from matches
        context_parts = []
        for match in results.matches:
            text = match.metadata.get("text", "")
            if text:
                context_parts.append(text)
        
        combined_context = "\n\n".join(context_parts)
        
        # Estimate tokens (rough: 4 chars = 1 token)
        estimated_tokens = len(combined_context) // 4
        
        return {
            "success": True,
            "context": combined_context,
            "sources_count": len(context_parts),
            "tokens_used": estimated_tokens,
            "error": None
        }
        
    except Exception as e:
        return {
            "success": False,
            "context": "",
            "sources_count": 0,
            "tokens_used": 0,
            "error": str(e)
        }


# =============================================================================
# TOOL 2: WEB SEARCH (OPTIONAL)
# =============================================================================

@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
def web_search_tool(
    query: str,
    duration: int,
    language: str
) -> Dict[str, Any]:
    """
    Search web for additional context (only for videos > 10 minutes).
    
    Args:
        query: Search query
        duration: Video duration in minutes
        language: Detected language ("ru" or "en")
        
    Returns:
        {
            "success": bool,
            "context": str,
            "sources_count": int,
            "skipped": bool,  # True if duration <= 10 min or no API key
            "error": Optional[str]
        }
    """
    # Skip if duration <= threshold
    if duration <= WEB_SEARCH_DURATION_THRESHOLD:
        return {
            "success": True,
            "context": "",
            "sources_count": 0,
            "skipped": True,
            "error": None
        }
    
    # Skip if no API key
    serpapi_key = os.getenv("SERPAPI_API_KEY")
    if not serpapi_key:
        return {
            "success": True,
            "context": "",
            "sources_count": 0,
            "skipped": True,
            "error": "SERPAPI_API_KEY not set"
        }
    
    try:
        from serpapi import GoogleSearch
        
        # Perform search
        params = {
            "q": query,
            "api_key": serpapi_key,
            "num": 5,
            "hl": "ru" if language == "ru" else "en"
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # Extract organic results
        organic_results = results.get("organic_results", [])
        
        context_parts = []
        for result in organic_results:
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            if title and snippet:
                context_parts.append(f"{title}: {snippet}")
        
        combined_context = "\n\n".join(context_parts)
        
        return {
            "success": True,
            "context": combined_context,
            "sources_count": len(context_parts),
            "skipped": False,
            "error": None
        }
        
    except Exception as e:
        return {
            "success": False,
            "context": "",
            "sources_count": 0,
            "skipped": False,
            "error": str(e)
        }


# =============================================================================
# TOOL 3: SYNTHESIZE CONTEXT
# =============================================================================

def synthesize_tool(
    retrieved_context: str,
    web_context: str,
    genre: str,
    idea: str,
    language: str
) -> Dict[str, Any]:
    """
    Combine retrieved Pinecone context + web context into unified prompt.
    
    Args:
        retrieved_context: Text from Pinecone
        web_context: Text from web search
        genre: Story genre
        idea: Story idea
        language: Detected language
        
    Returns:
        {
            "success": bool,
            "synthesized_context": str,
            "tokens_used": int
        }
    """
    try:
        from langchain_core.messages import SystemMessage, HumanMessage
        
        # Initialize LLM (reused from cache)
        llm = get_llm(temperature=0.7)
        
        # Build synthesis prompt
        lang_instruction = "Respond in Russian" if language == "ru" else "Respond in English"
        
        system_prompt = f"""You are an expert storytelling consultant. Synthesize the provided context into key insights relevant to creating a {genre} script.

{lang_instruction}.

Focus on:
- Genre-specific storytelling techniques
- Narrative structure patterns
- Character development approaches
- Pacing and timing strategies"""

        user_prompt = f"""Story Idea: {idea}
Genre: {genre}

Best Practices from Knowledge Base:
{retrieved_context}

Additional Context from Web:
{web_context if web_context else "(No web context)"}

Synthesize the most relevant insights for this specific story."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        # Call LLM
        response = llm.invoke(messages)
        synthesized_text = response.content
        
        # Estimate tokens (prompt + completion)
        prompt_tokens = (len(system_prompt) + len(user_prompt)) // 4
        completion_tokens = len(synthesized_text) // 4
        total_tokens = prompt_tokens + completion_tokens
        
        return {
            "success": True,
            "synthesized_context": synthesized_text,
            "tokens_used": total_tokens
        }
        
    except Exception as e:
        return {
            "success": False,
            "synthesized_context": "",
            "tokens_used": 0,
            "error": str(e)
        }


# =============================================================================
# TOOL 3.5: REASONING (ReAct - Plan Creative Strategy)
# =============================================================================

@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
def reasoning_tool(
    genre: str,
    idea: str,
    duration: int,
    synthesized_context: str,
    language: str
) -> Dict[str, Any]:
    """
    Analyze context and decide creative strategy (ReAct reasoning step).
    
    This tool adds ReAct-style reasoning: the agent "thinks" about the best
    approach before generating the outline/script.
    
    Args:
        genre: Story genre
        idea: Story idea
        duration: Target duration
        synthesized_context: Synthesized best practices
        language: Detected language
        
    Returns:
        {
            "success": bool,
            "reasoning": str,  # Agent's reasoning trace
            "strategy": dict,  # Strategic decisions
            "tokens_used": int,
            "error": Optional[str]
        }
    """
    try:
        from langchain_core.messages import SystemMessage, HumanMessage
        
        # Initialize LLM (reused from cache)
        llm = get_llm(temperature=0.7)
        
        # Build reasoning prompt
        lang_instruction = "Respond in Russian" if language == "ru" else "Respond in English"
        
        system_prompt = f"""You are a creative director planning a {genre} video script.

{lang_instruction}.

Analyze the provided context and story idea, then decide on the optimal creative strategy.

Think step-by-step:
1. What makes this story compelling in the {genre} genre?
2. What tone and atmosphere should we establish?
3. What pacing approach works best for {duration} minute(s)?
4. Should we emphasize character psychology, plot twists, or atmosphere?
5. What specific techniques from the context should we prioritize?

Output your reasoning as a strategic plan."""

        user_prompt = f"""Story Idea: {idea}
Genre: {genre}
Duration: {duration} minute(s)

Context & Best Practices:
{synthesized_context[:2000]}...

Analyze this and provide:
1. Your reasoning about the best approach
2. Key strategic decisions (tone, pacing, emphasis)
3. Specific techniques to apply"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        # Call LLM for reasoning
        response = llm.invoke(messages)
        reasoning_text = response.content
        
        # Parse strategy from reasoning (simple heuristic-based extraction)
        strategy = {
            "tone": "atmospheric" if "atmospher" in reasoning_text.lower() else "direct",
            "pacing": "slow-build" if "gradual" in reasoning_text.lower() or "slow" in reasoning_text.lower() else "fast-paced",
            "emphasis": "character" if "character" in reasoning_text.lower() else "plot",
            "key_techniques": []
        }
        
        # Extract key techniques mentioned
        techniques = []
        if "tension" in reasoning_text.lower():
            techniques.append("tension-building")
        if "twist" in reasoning_text.lower():
            techniques.append("plot-twists")
        if "psycholog" in reasoning_text.lower():
            techniques.append("psychological-depth")
        if "visual" in reasoning_text.lower():
            techniques.append("visual-storytelling")
        
        strategy["key_techniques"] = techniques[:3]  # Top 3
        
        # Estimate tokens
        prompt_tokens = (len(system_prompt) + len(user_prompt)) // 4
        completion_tokens = len(reasoning_text) // 4
        total_tokens = prompt_tokens + completion_tokens
        
        return {
            "success": True,
            "reasoning": reasoning_text,
            "strategy": strategy,
            "tokens_used": total_tokens,
            "error": None
        }
        
    except Exception as e:
        return {
            "success": False,
            "reasoning": "",
            "strategy": {},
            "tokens_used": 0,
            "error": str(e)
        }


# =============================================================================
# TOOL 4: GENERATE OUTLINE
# =============================================================================

@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
def generate_outline_tool(
    genre: str,
    idea: str,
    duration: int,
    synthesized_context: str,
    language: str,
    target_chars: int,
    reasoning_strategy: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate script outline using LLM.
    
    Args:
        genre: Story genre
        idea: Story idea
        duration: Target duration in minutes
        synthesized_context: Synthesized best practices
        language: Detected language
        target_chars: Target character count
        reasoning_strategy: Strategic reasoning from reasoning_tool (optional)
        
    Returns:
        {
            "success": bool,
            "outline": str,
            "tokens_used": int,
            "error": Optional[str]
        }
    """
    try:
        from langchain_core.messages import SystemMessage, HumanMessage
        
        # Initialize LLM (reused from cache)
        llm = get_llm(temperature=OUTLINE_TEMPERATURE, max_tokens=MAX_OUTLINE_TOKENS)
        
        # Build outline prompt
        lang_instruction = "Create outline in Russian" if language == "ru" else "Create outline in English"
        
        # Add strategy guidance if available
        strategy_note = ""
        if reasoning_strategy:
            strategy_note = f"\n\nSTRATEGIC DIRECTION:\n{reasoning_strategy}\n\nFollow this strategic approach in your outline."
        
        system_prompt = f"""You are an expert screenwriter creating a {genre} script outline.

{lang_instruction}.

Create a detailed outline with:
- Clear 3-act structure
- Key scenes and beats
- Character arcs
- Pacing notes{strategy_note}

Target duration: {duration} minutes
Target length: ~{target_chars:,} characters"""

        user_prompt = f"""Story Idea:
{idea}

Best Practices & Context:
{synthesized_context}

Create a comprehensive outline for a {duration}-minute {genre} script."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        # Call LLM
        response = llm.invoke(messages)
        outline_text = response.content
        
        # Estimate tokens
        prompt_tokens = (len(system_prompt) + len(user_prompt)) // 4
        completion_tokens = len(outline_text) // 4
        total_tokens = prompt_tokens + completion_tokens
        
        return {
            "success": True,
            "outline": outline_text,
            "tokens_used": total_tokens,
            "error": None
        }
        
    except Exception as e:
        return {
            "success": False,
            "outline": "",
            "tokens_used": 0,
            "error": str(e)
        }


# =============================================================================
# TOOL 5: GENERATE SCRIPT
# =============================================================================

@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
def generate_script_tool(
    outline: str,
    genre: str,
    idea: str,
    duration: int,
    language: str,
    target_chars: int,
    iteration: int = 0,
    adjustment_instruction: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate full script from outline.
    
    Args:
        outline: Generated outline
        genre: Story genre
        idea: Story idea
        duration: Target duration
        language: Detected language
        target_chars: Target character count
        iteration: Current iteration number
        adjustment_instruction: Length adjustment instructions (if regenerating)
        
    Returns:
        {
            "success": bool,
            "script": str,
            "char_count": int,
            "tokens_used": int,
            "error": Optional[str]
        }
    """
    try:
        from langchain_core.messages import SystemMessage, HumanMessage
        
        # Calculate dynamic max_tokens based on target length
        max_tokens = calculate_max_script_tokens(target_chars)
        
        # Initialize LLM (reused from cache)
        llm = get_llm(temperature=SCRIPT_TEMPERATURE, max_tokens=max_tokens)
        
        # Build script prompt
        lang_instruction = "Write script in Russian" if language == "ru" else "Write script in English"
        
        iteration_note = f"\n\n(Iteration {iteration + 1})" if iteration > 0 else ""
        adjustment_note = f"\n\nADJUSTMENT NEEDED:\n{adjustment_instruction}" if adjustment_instruction else ""
        
        system_prompt = f"""You are a professional screenwriter creating a {genre} video script.

{lang_instruction}.

STORYTELLING GUIDELINES:
Generate a story in the format of artistic storytelling. This should be an emotionally rich, captivating story that is perceived as a real event that happened in life. The text should evoke empathy, tension, internal response, create the effect of presence and gradual disclosure of the situation. The story should be written in vivid literary language with attention to details, atmosphere, internal experiences and motivations of the characters.

Format strictly as continuous text. Do not use scene numbering, headings, time stamps, actor designations, stage directions or any structural elements. Only a cohesive artistic text of the story without explanations, comments and technical inserts.

Requirements:
- Target duration: {duration} minutes
- Target length: {target_chars:,} characters (STRICT - aim for 90-110% of target)
- Follow provided outline closely
- Include vivid descriptions and natural dialogue
- Maintain consistent pacing{iteration_note}{adjustment_note}"""

        user_prompt = f"""Story Idea:
{idea}

Outline:
{outline}

Write the complete {duration}-minute {genre} script. Aim for exactly {target_chars:,} characters."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        # Call LLM
        response = llm.invoke(messages)
        script_text = response.content
        char_count = len(script_text)
        
        # Estimate tokens
        prompt_tokens = (len(system_prompt) + len(user_prompt)) // 4
        completion_tokens = len(script_text) // 4
        total_tokens = prompt_tokens + completion_tokens
        
        return {
            "success": True,
            "script": script_text,
            "char_count": char_count,
            "tokens_used": total_tokens,
            "error": None
        }
        
    except Exception as e:
        return {
            "success": False,
            "script": "",
            "char_count": 0,
            "tokens_used": 0,
            "error": str(e)
        }


# =============================================================================
# TOOL 6: VALIDATE SCRIPT LENGTH
# =============================================================================

def validate_tool(
    script: str,
    target_chars: int
) -> Dict[str, Any]:
    """
    Validate script length against target (90-110% tolerance).
    
    Args:
        script: Generated script
        target_chars: Target character count
        
    Returns:
        {
            "success": bool,
            "is_valid": bool,
            "actual_chars": int,
            "target_chars": int,
            "ratio": float,
            "message": str
        }
    """
    actual_chars = len(script)
    is_valid, ratio, message = validate_script_length(actual_chars, target_chars)
    
    return {
        "success": True,
        "is_valid": is_valid,
        "actual_chars": actual_chars,
        "target_chars": target_chars,
        "ratio": ratio,
        "message": message
    }


# =============================================================================
# TOOL 7: REGENERATE SCRIPT
# =============================================================================

def regenerate_tool(
    outline: str,
    genre: str,
    idea: str,
    duration: int,
    language: str,
    target_chars: int,
    actual_chars: int,
    iteration: int
) -> Dict[str, Any]:
    """
    Regenerate script with length adjustment instructions.
    
    Args:
        outline: Original outline
        genre: Story genre
        idea: Story idea
        duration: Target duration
        language: Detected language
        target_chars: Target character count
        actual_chars: Current character count
        iteration: Current iteration number
        
    Returns:
        Same as generate_script_tool + adjustment_instruction used
    """
    # Get adjustment instruction
    adjustment_instruction = get_length_adjustment_instruction(
        actual_chars,
        target_chars
    )
    
    # Call generate_script_tool with adjustment
    result = generate_script_tool(
        outline=outline,
        genre=genre,
        idea=idea,
        duration=duration,
        language=language,
        target_chars=target_chars,
        iteration=iteration,
        adjustment_instruction=adjustment_instruction
    )
    
    # Add adjustment instruction to result
    result["adjustment_instruction"] = adjustment_instruction
    
    return result


# =============================================================================
# TOOL REGISTRY
# =============================================================================

TOOLS = {
    "retrieve": retrieve_tool,
    "web_search": web_search_tool,
    "synthesize": synthesize_tool,
    "generate_outline": generate_outline_tool,
    "generate_script": generate_script_tool,
    "validate": validate_tool,
    "regenerate": regenerate_tool,
}


# =============================================================================
# TOOL 9: SEGMENT SCRIPT (NEW - Phase 2)
# =============================================================================

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def segment_script_tool(
    script: str,
    language: str
) -> Dict[str, Any]:
    """
    Segment script into 2-6 sentence visual moments using Cohere.
    
    Each segment should represent a distinct narrative moment that can be
    illustrated with a single static image.
    
    Args:
        script: Full generated script text
        language: Detected language ("ru" or "en")
        
    Returns:
        {
            "success": bool,
            "segments": List[Dict],  # [{"index": 1, "text": "..."}]
            "segment_count": int,
            "tokens_used": int,
            "error": Optional[str]
        }
    """
    try:
        import cohere
        
        logger.info(f"Starting script segmentation (language: {language}, script length: {len(script)} chars)")
        
        # Initialize Cohere client
        co = cohere.ClientV2(api_key=os.getenv("COHERE_API_KEY"))
        
        # Build segmentation prompt
        if language == "ru":
            system_prompt = """Вы — движок для кинематографической сегментации истории.
Ваша задача — разбить историю на короткие повествовательные сегменты, оптимизированные для визуализации сцен.
Каждый сегмент должен представлять собой один четкий визуальный момент, который можно изобразить в виде одного статичного изображения.
Цель — подготовить историю для генерации изображений AI, сторибордов или пайплайнов типа image-to-video.

ВАЖНЫЕ ПРАВИЛА

1. Один визуальный момент на сегмент
Каждый сегмент должен представлять одну сцену или действие, которое реально можно зафиксировать на одном статичном изображении.

2. Избегайте нескольких событий в одном сегменте
Если абзац содержит несколько действий, разделяйте их на отдельные сегменты.

3. Предпочитайте визуальную ясность
Каждый сегмент должен четко описывать:
• кто присутствует
• что они делают
• окружение / среду
• эмоциональный тон или напряжение

4. Держите сегменты короткими
Идеальная длина: 1–5 предложений.
Максимум: 5 предложений, только если они описывают один и тот же визуальный момент.

5. Разделяйте сегменты, когда меняется:
• новое действие
• новый персонаж появляется
• меняется эмоциональное напряжение
• меняется точка фокусировки (камеры)
• меняется композиция сцены

6. Сохраняйте точный оригинальный текст
• НЕ переписывайте и не сокращайте текст.
• Только разделяйте существующий текст на части.

7. Сохраняйте порядок событий
Сегменты должны следовать в том же порядке, что и оригинальная история.

8. Избегайте слишком маленьких фрагментов
Не делите на отдельные фразы, если это не необходимо для визуальной ясности.

Определяйте подходящее количество сегментов исходя из структуры и длины текста.

КРИТИЧЕСКИ ВАЖНЫЕ ПРАВИЛА КОПИРОВАНИЯ ТЕКСТА:
1. КОПИРУЙТЕ текст символ в символ из оригинала.
2. НЕ меняйте слова, пунктуацию или форматирование.
3. НЕ добавляйте новые предложения.
4. НЕ перефразируйте текст.
5. Просто разделите СУЩЕСТВУЮЩИЙ текст на части.

ПРАВИЛЬНЫЙ пример:
Оригинал: "Привет, мир! Как дела? Отлично."
Сегмент 1: "Привет, мир!" ✓ (точная копия)
Сегмент 2: "Как дела? Отлично." ✓ (точная копия)

НЕПРАВИЛЬНО:
"Приветствую мир!" ✗ (изменено)
"Как у тебя дела?" ✗ (перефразировано)

Формат ответа — ТОЛЬКО валидный JSON:
[
  {"index": 1, "text": "ТОЧНАЯ копия текста из оригинала"},
  {"index": 2, "text": "ТОЧНАЯ копия следующей части"}
]"""

            user_prompt = f"""Вы — движок для кинематографической сегментации истории.
Ваша задача — разбить историю на короткие повествовательные сегменты, оптимизированные для визуализации сцен.
Каждый сегмент должен представлять собой один четкий визуальный момент, который можно изобразить в виде одного статичного изображения.
Цель — подготовить историю для генерации изображений AI, сторибордов или пайплайнов типа image-to-video.

ВАЖНЫЕ ПРАВИЛА

1. Один визуальный момент на сегмент
Каждый сегмент должен представлять одну сцену или действие, которое реально можно зафиксировать на одном статичном изображении.

2. Избегайте нескольких событий в одном сегменте
Если абзац содержит несколько действий, разделяйте их на отдельные сегменты.

3. Предпочитайте визуальную ясность
Каждый сегмент должен четко описывать:
• кто присутствует
• что они делают
• окружение / среду
• эмоциональный тон или напряжение

4. Держите сегменты короткими
Идеальная длина: 1–5 предложений.
Максимум: 5 предложений, только если они описывают один и тот же визуальный момент.

5. Разделяйте сегменты, когда меняется:
• новое действие
• новый персонаж появляется
• меняется эмоциональное напряжение
• меняется точка фокусировки (камеры)
• меняется композиция сцены

6. Сохраняйте точный оригинальный текст
• НЕ переписывайте и не сокращайте текст.
• Только разделяйте существующий текст на части.

7. Сохраняйте порядок событий
Сегменты должны следовать в том же порядке, что и оригинальная история.

8. Избегайте слишком маленьких фрагментов
Не делите на отдельные фразы, если это не необходимо для визуальной ясности.

9. Избегайте абстрактных или невизуальных предложений как отдельных сегментов
Если предложение описывает только эмоцию, атмосферу или нарратив, объедините его с ближайшим визуальным моментом.

10. Избегайте сегментов короче 50 символов
Предпочитайте объединение очень маленьких фрагментов (менее 50 символов) с предыдущим визуальным моментом, если это не абсолютно необходимо.

ПЕРЕД ФИНАЛИЗАЦИЕЙ СЕГМЕНТАЦИИ ПРОВЕРЬ:

1. Каждый сегмент представляет один визуальный момент.
2. Каждый сегмент реально можно проиллюстрировать как одно статичное изображение.
3. Ни один сегмент не содержит несколько различных действий.
4. Ни один сегмент не является чисто абстрактным повествованием.

Определяйте подходящее количество сегментов исходя из структуры и длины текста.

КРИТИЧЕСКИ ВАЖНЫЕ ПРАВИЛА КОПИРОВАНИЯ ТЕКСТА:
1. КОПИРУЙТЕ текст символ в символ из оригинала.
2. НЕ меняйте слова, пунктуацию или форматирование.
3. НЕ добавляйте новые предложения.
4. НЕ перефразируйте текст.
5. Просто разделите СУЩЕСТВУЮЩИЙ текст на части.

ПРАВИЛЬНЫЙ пример:
Оригинал: "Привет, мир! Как дела? Отлично."
Сегмент 1: "Привет, мир!" ✓ (точная копия)
Сегмент 2: "Как дела? Отлично." ✓ (точная копия)

НЕПРАВИЛЬНО:
"Приветствую мир!" ✗ (изменено)
"Как у тебя дела?" ✗ (перефразировано)

Формат ответа — ТОЛЬКО валидный JSON:
[
  {{"index": 1, "text": "ТОЧНАЯ копия текста из оригинала"}},
  {{"index": 2, "text": "ТОЧНАЯ копия следующей части"}}
]

⚠️⚠️⚠️ ЗАДАЧА: Разбей этот сценарий на визуальные сегменты ⚠️⚠️⚠️

⚠️ КРИТИЧЕСКИ ВАЖНО: КОПИРУЙ ТЕКСТ БУКВА В БУКВУ! НЕ ПЕРЕПИСЫВАЙ!

Исходный текст для сегментации:

{script}

Напоминание: Не меняй ни одного слова!"""
        else:
            system_prompt = """You are a cinematic story segmentation engine.
Your task is to split a story into short narrative segments optimized for visual scene generation.
Each segment must represent one clear visual moment that can be illustrated with a single static image.
The goal is to prepare the story for AI image generation, storyboards, or image-to-video pipelines.

IMPORTANT RULES

1. One visual moment per segment
Each segment must represent a single scene or action that could realistically be captured in one still image.

2. Avoid multiple events in one segment
If a paragraph contains several actions, split them into separate segments.

3. Prefer visual clarity
Each segment should clearly describe:
• who is present
• what they are doing
• the environment
• the emotional tone or tension

4. Keep segments short
Ideal length: 1–5 sentences.
Maximum: 5 sentences only if they describe the same visual moment.

5. Split when any of the following changes
• a new action begins
• a new character appears
• the emotional tension changes
• the camera focus would change
• the scene composition changes

6. Maintain the exact original text
Do NOT rewrite, summarize, or change wording.
Only divide the original text into smaller segments.

7. Preserve story order
Segments must follow the original narrative sequence.

8. Avoid extremely tiny fragments
Do not split into single clauses unless necessary for visual clarity.

Determine the appropriate number of segments based on the structure and length of the script.

CRITICALLY IMPORTANT — TEXT COPYING RULES:
1. COPY the text CHARACTER BY CHARACTER from the original
2. DO NOT change any words, punctuation, or formatting
3. DO NOT add new sentences
4. DO NOT paraphrase or rewrite anything
5. Simply split the EXISTING text into parts

CORRECT example:
Original: "Hello world! How are you? Great."
Segment 1: "Hello world!" ✓ (exact copy)
Segment 2: "How are you? Great." ✓ (exact copy)

INCORRECT:
"Greetings world!" ✗ (changed wording)
"How are things?" ✗ (paraphrased)

Response format — ONLY valid JSON:
[
  {"index": 1, "text": "EXACT copy of text from the original"},
  {"index": 2, "text": "EXACT copy of the next part"}
]"""

            user_prompt = f"""You are a cinematic story segmentation engine.
Your task is to split a story into short narrative segments optimized for visual scene generation.
Each segment must represent one clear visual moment that can be illustrated with a single static image.
The goal is to prepare the story for AI image generation, storyboards, or image-to-video pipelines.

IMPORTANT RULES

1. One visual moment per segment
Each segment must represent a single scene or action that could realistically be captured in one still image.

2. Avoid multiple events in one segment
If a paragraph contains several actions, split them into separate segments.

3. Prefer visual clarity
Each segment should clearly describe:
• who is present
• what they are doing
• the environment
• the emotional tone or tension

4. Keep segments short
Ideal length: 1–5 sentences.
Maximum: 5 sentences only if they describe the same visual moment.

5. Split when any of the following changes
• a new action begins
• a new character appears
• the emotional tension changes
• the camera focus would change
• the scene composition changes

6. Maintain the exact original text
Do NOT rewrite, summarize, or change wording.
Only divide the original text into smaller segments.

7. Preserve story order
Segments must follow the original narrative sequence.

8. Avoid extremely tiny fragments
Do not split into single clauses unless necessary for visual clarity.

9. Avoid abstract or non-visual sentences as standalone segments
If a sentence describes only emotion, atmosphere, or narration, merge it with a nearby visual moment.

10. Avoid segments shorter than 50 characters
Prefer merging very small fragments (less than 50 characters) with the previous visual moment unless absolutely necessary.

BEFORE FINALIZING THE SEGMENTATION, VERIFY:

1. Each segment represents a single visual moment.
2. Each segment could realistically be illustrated as a single static image.
3. No segment contains multiple distinct actions.
4. No segment is purely abstract narration.

Determine the appropriate number of segments based on the structure and length of the script.

CRITICALLY IMPORTANT — TEXT COPYING RULES:
1. COPY the text CHARACTER BY CHARACTER from the original
2. DO NOT change any words, punctuation, or formatting
3. DO NOT add new sentences
4. DO NOT paraphrase or rewrite anything
5. Simply split the EXISTING text into parts

CORRECT example:
Original: "Hello world! How are you? Great."
Segment 1: "Hello world!" ✓ (exact copy)
Segment 2: "How are you? Great." ✓ (exact copy)

INCORRECT:
"Greetings world!" ✗ (changed wording)
"How are things?" ✗ (paraphrased)

Response format — ONLY valid JSON:
[
  {{"index": 1, "text": "EXACT copy of text from the original"}},
  {{"index": 2, "text": "EXACT copy of the next part"}}
]

⚠️⚠️⚠️ TASK: Split this script into visual segments ⚠️⚠️⚠️

⚠️ CRITICALLY IMPORTANT: COPY TEXT CHARACTER BY CHARACTER! DO NOT REWRITE!

Original text to segment:

{script}

Reminder: Do not change any words!"""
        
        # Call Cohere Chat API
        response = co.chat(
            model="command-r-08-2024",  # Current Command-R model for structured tasks
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0,  # Zero temperature = deterministic, no creativity
            max_tokens=4000  # Command-R-08-2024 max is 4096
        )
        
        # Extract response text
        response_text = response.message.content[0].text
        
        # Parse JSON response
        # Remove markdown code blocks if present
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        segments = json.loads(response_text)
        
        # Validate structure
        if not isinstance(segments, list):
            raise ValueError("Cohere response is not a list")
        
        if len(segments) == 0:
            raise ValueError("No segments returned")
        
        # Validate each segment
        validated_segments = []
        for seg in segments:
            if not isinstance(seg, dict):
                continue
            if "index" not in seg or "text" not in seg:
                continue
            
            # Normalize keys
            validated_segments.append({
                "segment_index": seg["index"],
                "text": seg["text"].strip()
            })
        
        if len(validated_segments) == 0:
            raise ValueError("No valid segments after validation")
        
        # CRITICAL VALIDATION: Check if segments contain original text
        # Combine all segment texts and compare with original
        combined_text = " ".join([seg["text"] for seg in validated_segments])
        
        # Extract first 50 chars from original and check if they appear in segments
        original_sample = script[:50].strip()
        if original_sample and original_sample not in combined_text:
            # LLM did rewrite instead of copy!
            error_msg = f"Segmentation validation FAILED: Cohere rewrote the text instead of preserving it. Original start: '{original_sample}...' not found in segments."
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Check character count similarity (should be ~same, allowing for whitespace)
        original_chars = len(script.replace(" ", "").replace("\n", ""))
        combined_chars = len(combined_text.replace(" ", "").replace("\n", ""))
        char_diff_percent = abs(original_chars - combined_chars) / original_chars * 100
        
        if char_diff_percent > 15:  # More than 15% difference = likely rewrite
            error_msg = f"Segmentation validation FAILED: Character count mismatch {char_diff_percent:.1f}% (original: {original_chars}, segments: {combined_chars}). Text was likely rewritten."
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Estimate tokens used (input + output)
        tokens_used = (len(script) + len(response_text)) // 4
        
        logger.info(f"Segmentation successful: {len(validated_segments)} segments created, {tokens_used} tokens used")
        logger.info(f"✓ Validation passed: Original text preserved (char diff: {char_diff_percent:.1f}%)")
        
        return {
            "success": True,
            "segments": validated_segments,
            "segment_count": len(validated_segments),
            "tokens_used": tokens_used,
            "error": None
        }
        
    except json.JSONDecodeError as e:
        # Fallback: Simple sentence-based segmentation
        logger.warning(f"Cohere JSON parsing failed, using fallback: {e}")
        print(f"  ⚠️  Cohere JSON parsing failed, using fallback: {e}")
        return _fallback_sentence_segmentation(script)
        
    except Exception as e:
        error_msg = f"Segmentation failed: {str(e)}"
        logger.error(error_msg)
        print(f"  ✗ {error_msg}")
        
        # Fallback to sentence splitting
        return _fallback_sentence_segmentation(script)


def _fallback_sentence_segmentation(script: str) -> Dict[str, Any]:
    """
    Fallback segmentation using simple sentence splitting.
    
    Used when Cohere API fails or returns invalid JSON.
    
    Args:
        script: Full script text
        
    Returns:
        Same format as segment_script_tool()
    """
    import re
    
    # Split by sentence endings
    sentences = re.split(r'(?<=[.!?])\s+', script)
    
    # Group sentences into segments (4 sentences per segment)
    segments = []
    segment_index = 1
    
    for i in range(0, len(sentences), 4):
        segment_text = " ".join(sentences[i:i+4])
        if segment_text.strip():
            segments.append({
                "segment_index": segment_index,
                "text": segment_text.strip()
            })
            segment_index += 1
    
    return {
        "success": True,
        "segments": segments,
        "segment_count": len(segments),
        "tokens_used": 0,  # Fallback doesn't use API tokens
        "error": "Used fallback segmentation (Cohere unavailable)"
    }


# =============================================================================
# TOOL 10: GENERATE AUDIO (NEW - Phase 2)
# =============================================================================

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def generate_tts_tool(
    segments: List[Dict[str, Any]],
    project_name: str,
    audio_base_url: str,
    voice: str = "alloy"
) -> Dict[str, Any]:
    """
    Generate TTS audio files for all segments using OpenAI.
    
    Creates audio files in: projects/{project_slug}/000X.mp3
    Returns public URLs accessible via tunnel.
    
    Args:
        segments: List of segment dicts with segment_index and text
        project_name: Project name for directory creation
        audio_base_url: Base URL detected from request (e.g., https://tunnel.com)
        voice: OpenAI TTS voice (default: alloy)
        
    Returns:
        {
            "success": bool,
            "segments": List[Dict],  # Updated with audio_url field
            "audio_files": List[str],  # Local file paths
            "audio_files_count": int,
            "tokens_used": int,  # Always 0 for TTS
            "tts_characters": int,  # Total characters sent to TTS API
            "tts_estimated_cost": float,  # Estimated cost in USD
            "error": Optional[str]
        }
    """
    try:
        from openai import OpenAI
        from pathlib import Path
        import glob
        
        # CRITICAL DEBUG: Log incoming segments
        logger.info(f"========== GENERATE_TTS_TOOL CALLED ==========")
        logger.info(f"Project: {project_name}")
        logger.info(f"Total segments received: {len(segments)}")
        logger.info(f"First 3 segments:")
        for i, seg in enumerate(segments[:3], 1):
            text = seg.get('text', '')
            logger.info(f"  Segment {seg.get('segment_index', i)}: {text[:80]}... ({len(text)} chars)")
        print(f"\n  [TTS DEBUG] Received {len(segments)} segments for '{project_name}'")
        print(f"  [TTS DEBUG] First segment text: {segments[0].get('text', '')[:80] if segments else 'NONE'}...")
        
        # Initialize OpenAI client
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Create URL-safe project slug (replace spaces with underscores)
        project_slug = create_project_slug(project_name)
        
        # Create project directory (audio files go directly in project folder)
        project_dir = Path("projects") / project_slug
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # ⚠️ ВАЖНО: Удаляем ВСЕ старые MP3 файлы перед генерацией новых
        # Это гарантирует что будут только те файлы которые соответствуют текущим сегментам
        old_audio_files = list(project_dir.glob("*.mp3"))
        if old_audio_files:
            logger.info(f"Removing {len(old_audio_files)} old audio files from {project_dir}")
            print(f"  [TTS] Cleaning up {len(old_audio_files)} old audio files...")
            for old_file in old_audio_files:
                try:
                    old_file.unlink()
                except Exception as e:
                    logger.warning(f"Failed to remove {old_file}: {e}")
        
        logger.info(f"Generating TTS audio for {len(segments)} segments in: {project_dir}")
        
        # Generate audio for each segment
        updated_segments = []
        audio_files = []
        failed_segments = []
        total_tts_characters = 0  # Track total characters sent to TTS
        
        for seg in segments:
            segment_index = seg.get("segment_index")
            text = seg.get("text")
            
            if not text or not segment_index:
                logger.warning(f"Skipping invalid segment: {seg}")
                print(f"  ⚠️  Skipping invalid segment: {seg}")
                continue
            
            # Generate filename: 0001.mp3, 0002.mp3, etc.
            filename = f"{segment_index:04d}.mp3"
            file_path = project_dir / filename
            
            # Check if file already exists (idempotency)
            if file_path.exists():
                logger.info(f"Audio file already exists: {filename}")
                print(f"  ℹ  Audio file already exists: {filename}")
                audio_url = f"{audio_base_url}/projects/{project_slug}/{filename}"
                updated_segments.append({
                    "segment_index": segment_index,
                    "text": text,
                    "audio_url": audio_url
                })
                audio_files.append(str(file_path))
                continue
            
            try:
                # Generate TTS audio
                logger.info(f"Generating TTS for segment {segment_index}: {len(text)} chars")
                logger.info(f"  EXACT TEXT BEING SENT TO TTS: '{text[:150]}...'")
                print(f"  [TTS] Segment {segment_index}: Sending to OpenAI TTS: '{text[:60]}...' ({len(text)} chars)")
                
                response = client.audio.speech.create(
                    model="tts-1",
                    voice=voice,
                    input=text,
                    response_format="mp3"
                )
                
                # Save audio file
                response.stream_to_file(str(file_path))
                
                # Track TTS characters
                total_tts_characters += len(text)
                
                # Build public URL
                audio_url = f"{audio_base_url}/projects/{project_slug}/{filename}"
                
                # Add to updated segments
                updated_segments.append({
                    "segment_index": segment_index,
                    "text": text,
                    "audio_url": audio_url
                })
                
                audio_files.append(str(file_path))
                print(f"  ✓ Generated: {filename} ({len(text)} chars)")
                
            except Exception as e:
                print(f"  ✗ Failed to generate audio for segment {segment_index}: {e}")
                failed_segments.append(segment_index)
                
                # Add segment without audio_url (partial failure)
                updated_segments.append({
                    "segment_index": segment_index,
                    "text": text,
                    "audio_url": ""  # Empty URL indicates failure
                })
        
        # Determine overall success
        total_segments = len(segments)
        successful_audio = len(audio_files)
        
        # Calculate estimated TTS cost (OpenAI TTS-1: $0.015 per 1,000 characters)
        tts_cost = (total_tts_characters / 1000) * 0.015
        
        if successful_audio == 0:
            # Complete audio failure
            return {
                "success": False,
                "segments": [],
                "audio_files": [],
                "audio_files_count": 0,
                "tokens_used": 0,
                "tts_characters": 0,
                "tts_estimated_cost": 0.0,
                "error": f"All audio generation failed ({total_segments} segments)"
            }
        
        # Partial or full success
        error_msg = None
        if failed_segments:
            error_msg = f"Partial success: {len(failed_segments)} segment(s) failed: {failed_segments}"
        
        logger.info(f"TTS generation complete: {successful_audio}/{total_segments} segments, {total_tts_characters:,} characters, estimated cost: ${tts_cost:.4f}")
        
        return {
            "success": successful_audio > 0,
            "segments": updated_segments,
            "audio_files": audio_files,
            "audio_files_count": successful_audio,
            "tokens_used": 0,  # TTS doesn't use completion tokens
            "tts_characters": total_tts_characters,
            "tts_estimated_cost": round(tts_cost, 4),
            "error": error_msg
        }
        
    except Exception as e:
        error_msg = f"Audio generation failed: {str(e)}"
        print(f"  ✗ {error_msg}")
        
        return {
            "success": False,
            "segments": [],
            "audio_files": [],
            "audio_files_count": 0,
            "tokens_used": 0,
            "tts_characters": 0,
            "tts_estimated_cost": 0.0,
            "error": error_msg
        }


# Update TOOLS registry
TOOLS["segment_script"] = segment_script_tool
TOOLS["generate_audio"] = generate_tts_tool


def get_tool(tool_name: str):
    """Get tool function by name."""
    return TOOLS.get(tool_name)


def list_tools() -> List[str]:
    """List all available tool names."""
    return list(TOOLS.keys())


# =============================================================================
# CLI FOR TESTING
# =============================================================================

if __name__ == "__main__":
    """Test tools with sample inputs."""
    print("=" * 80)
    print("AGENT TOOLS TEST")
    print("=" * 80)
    
    # Check environment variables
    print("\n1. Checking environment variables:")
    print("-" * 80)
    
    env_vars = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "PINECONE_API_KEY": os.getenv("PINECONE_API_KEY"),
        "COHERE_API_KEY": os.getenv("COHERE_API_KEY"),
        "SERPAPI_API_KEY": os.getenv("SERPAPI_API_KEY"),
    }
    
    for var_name, var_value in env_vars.items():
        status = "✓" if var_value else "✗"
        display_value = f"{var_value[:8]}..." if var_value else "(not set)"
        print(f"  {status} {var_name}: {display_value}")
    
    # Test tool registry
    print("\n2. Testing tool registry:")
    print("-" * 80)
    
    available_tools = list_tools()
    print(f"  Available tools: {len(available_tools)}")
    for i, tool_name in enumerate(available_tools, 1):
        tool_func = get_tool(tool_name)
        print(f"    {i}. {tool_name} → {tool_func.__name__}")
    
    # Test retrieve tool (if keys available)
    print("\n3. Testing retrieve_tool:")
    print("-" * 80)
    
    if env_vars["PINECONE_API_KEY"] and env_vars["COHERE_API_KEY"]:
        try:
            result = retrieve_tool(
                query="Comedy storytelling best practices",
                language="en",
                top_k=3
            )
            print(f"  Success: {result['success']}")
            print(f"  Sources: {result['sources_count']}")
            print(f"  Context length: {len(result['context'])} chars")
            print(f"  Tokens used: {result['tokens_used']}")
            if result.get('error'):
                print(f"  Error: {result['error']}")
        except Exception as e:
            print(f"  ✗ Failed: {e}")
    else:
        print("  ⊘ Skipped (missing API keys)")
    
    # Test web_search tool
    print("\n4. Testing web_search_tool:")
    print("-" * 80)
    
    result = web_search_tool(
        query="Comedy script structure",
        duration=5,  # Below threshold
        language="en"
    )
    print(f"  Success: {result['success']}")
    print(f"  Skipped: {result['skipped']} (duration <= 10 min)")
    
    result = web_search_tool(
        query="Comedy script structure",
        duration=15,  # Above threshold
        language="en"
    )
    print(f"  Success: {result['success']}")
    print(f"  Skipped: {result['skipped']} (duration > 10 min)")
    if result.get('error'):
        print(f"  Error: {result['error']}")
    
    # Test validate tool
    print("\n5. Testing validate_tool:")
    print("-" * 80)
    
    test_cases = [
        ("Valid script", "A" * 5000, 5000),
        ("Too short", "A" * 4000, 5000),
        ("Too long", "A" * 6000, 5000),
    ]
    
    for description, script, target in test_cases:
        result = validate_tool(script, target)
        print(f"  {description}:")
        print(f"    Valid: {result['is_valid']}")
        print(f"    Ratio: {result['ratio']:.1%}")
        print(f"    Message: {result['message']}")
    
    # Test synthesize tool (if OpenAI key available)
    print("\n6. Testing synthesize_tool:")
    print("-" * 80)
    
    if env_vars["OPENAI_API_KEY"]:
        try:
            result = synthesize_tool(
                retrieved_context="Use three-act structure. Start with a hook.",
                web_context="Comedy requires strong character setup.",
                genre="Comedy",
                idea="A programmer creates an AI",
                language="en"
            )
            print(f"  Success: {result['success']}")
            print(f"  Synthesized length: {len(result.get('synthesized_context', ''))} chars")
            print(f"  Tokens used: {result.get('tokens_used', 0)}")
            if result.get('error'):
                print(f"  Error: {result['error']}")
        except Exception as e:
            print(f"  ✗ Failed: {e}")
    else:
        print("  ⊘ Skipped (OPENAI_API_KEY not set)")
    
    # Test generate_outline tool (if OpenAI key available)
    print("\n7. Testing generate_outline_tool:")
    print("-" * 80)
    
    if env_vars["OPENAI_API_KEY"]:
        try:
            result = generate_outline_tool(
                genre="Comedy",
                idea="A programmer creates an AI that becomes self-aware",
                duration=5,
                synthesized_context="Use three-act structure with strong character setup",
                language="en",
                target_chars=5000
            )
            print(f"  Success: {result['success']}")
            print(f"  Outline length: {len(result.get('outline', ''))} chars")
            print(f"  Tokens used: {result.get('tokens_used', 0)}")
            if result.get('error'):
                print(f"  Error: {result['error']}")
        except Exception as e:
            print(f"  ✗ Failed: {e}")
    else:
        print("  ⊘ Skipped (OPENAI_API_KEY not set)")
    
    print("\n" + "=" * 80)
    print("✓ TOOLS TEST COMPLETE")
    print("=" * 80)

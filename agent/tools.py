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
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

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

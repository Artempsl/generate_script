"""
Pydantic models for Agent Backend request/response validation.

This module defines:
- Request models (from n8n)
- Response models (to n8n)
- AgentState TypedDict (for LangGraph)
- Validation rules
"""

from typing import Optional, List, Dict, Any, TypedDict
from pydantic import BaseModel, Field, field_validator
from uuid import uuid4


# =============================================================================
# REQUEST MODELS (from n8n)
# =============================================================================

class ScriptRequestItem(BaseModel):
    """
    Single script generation request (from n8n array).
    
    Matches n8n execution node output format.
    """
    
    isValid: bool = Field(
        ...,
        description="Validation status from n8n"
    )
    
    projectName: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Project name"
    )
    
    genre: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Story genre (e.g., Comedy, Drama, Sci-Fi)"
    )
    
    storyIdea: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Story concept/idea"
    )
    
    duration: int = Field(
        ...,
        ge=1,
        le=60,
        description="Target video duration in minutes (1-60)"
    )
    
    request_id: Optional[str] = Field(
        default=None,
        description="Unique request ID for idempotency"
    )
    
    @field_validator('request_id', mode='before')
    @classmethod
    def generate_request_id(cls, v):
        """Generate UUID if request_id not provided."""
        if v is None or v == "":
            return str(uuid4())
        return v
    
    @field_validator('isValid')
    @classmethod
    def check_is_valid(cls, v):
        """Ensure isValid is True."""
        if not v:
            raise ValueError("Request validation failed: isValid must be True")
        return v


class ScriptRequestArray(BaseModel):
    """
    n8n sends array of requests.
    
    For MVP, we process only the first item.
    """
    
    items: List[ScriptRequestItem] = Field(
        ...,
        min_length=1,
        description="Array of script generation requests"
    )
    
    @property
    def first_item(self) -> ScriptRequestItem:
        """Get first item (primary request)."""
        return self.items[0]


# =============================================================================
# RESPONSE MODELS (to n8n)
# =============================================================================

class ScriptResponse(BaseModel):
    """
    Response sent back to n8n execution node.
    """
    
    request_id: str = Field(
        ...,
        description="Unique request identifier"
    )
    
    status: str = Field(
        ...,
        description="Execution status: 'success' or 'error'"
    )
    
    script: Optional[str] = Field(
        default=None,
        description="Generated script content"
    )
    
    outline: Optional[str] = Field(
        default=None,
        description="Generated outline"
    )
    
    char_count: Optional[int] = Field(
        default=None,
        description="Character count of generated script"
    )
    
    duration_target: Optional[int] = Field(
        default=None,
        description="Target duration in minutes"
    )
    
    reasoning_trace: Optional[str] = Field(
        default=None,
        description="Summary of reasoning steps (full trace in database)"
    )
    
    iteration_count: Optional[int] = Field(
        default=None,
        description="Number of generation iterations"
    )
    
    tokens_used_total: Optional[int] = Field(
        default=None,
        description="Total tokens consumed (prompt + completion)"
    )
    
    retrieved_sources_count: Optional[int] = Field(
        default=None,
        description="Number of Pinecone sources retrieved"
    )
    
    error_message: Optional[str] = Field(
        default=None,
        description="Error message if status is 'error'"
    )


# =============================================================================
# LANGGRAPH STATE (TypedDict)
# =============================================================================

class ReasoningStep(TypedDict):
    """Single reasoning step in ReAct loop."""
    step: int
    action: str
    result: str
    tokens_used: int
    timestamp: str


class AgentState(TypedDict, total=False):
    """
    State object for LangGraph StateGraph.
    
    This state flows through all graph nodes and accumulates information.
    
    Note: TypedDict with total=False allows optional fields.
    """
    
    # Input fields (from request)
    request_id: str
    project_name: str
    genre: str
    idea: str
    duration: int
    
    # Detected/calculated fields
    language: str  # "ru" or "en"
    target_chars: int
    
    # Retrieved context
    retrieved_context: str
    web_context: str
    synthesized_context: str
    retrieved_sources_count: int
    
    # ReAct reasoning (NEW)
    reasoning: str  # Agent's reasoning trace
    reasoning_strategy: Dict[str, Any]  # Strategic decisions
    
    # Generated outputs
    outline: str
    script: str
    char_count: int
    
    # Validation
    validation_passed: bool
    validation_ratio: float
    validation_message: str
    
    # Control flow
    iteration: int
    max_iterations: int
    web_search_enabled: bool
    should_regenerate: bool
    
    # Tracking
    reasoning_trace: List[ReasoningStep]
    tokens_used: int
    
    # Error handling
    error: Optional[str]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def create_initial_state(request: ScriptRequestItem) -> AgentState:
    """
    Create initial agent state from request.
    
    Args:
        request: Validated request from n8n
        
    Returns:
        Initial AgentState with input fields populated
    """
    # Handle both module and standalone execution
    try:
        from agent.language_utils import detect_language, calculate_target_chars
    except ModuleNotFoundError:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from agent.language_utils import detect_language, calculate_target_chars
    
    # Detect language from genre + idea
    combined_text = f"{request.genre} {request.storyIdea}"
    language = detect_language(combined_text)
    target_chars = calculate_target_chars(request.duration, language)
    
    # Return dict instead of AgentState() for LangGraph compatibility
    return {
        "request_id": request.request_id or str(uuid4()),
        "project_name": request.projectName,
        "genre": request.genre,
        "idea": request.storyIdea,
        "duration": request.duration,
        "language": language,
        "target_chars": target_chars,
        "retrieved_context": "",
        "web_context": "",
        "synthesized_context": "",
        "retrieved_sources_count": 0,
        "reasoning": "",  # NEW: ReAct reasoning
        "reasoning_strategy": {},  # NEW: Strategic decisions
        "outline": "",
        "script": "",
        "char_count": 0,
        "validation_passed": False,
        "validation_ratio": 0.0,
        "validation_message": "",
        "iteration": 0,
        "max_iterations": 3,
        "web_search_enabled": request.duration > 10,
        "should_regenerate": False,
        "reasoning_trace": [],
        "tokens_used": 0,
        "error": None,
    }


def state_to_response(state: AgentState) -> ScriptResponse:
    """
    Convert agent state to API response.
    
    Args:
        state: Final agent state after execution
        
    Returns:
        ScriptResponse for n8n
    """
    # Determine status
    status = "success" if state.get("script") and not state.get("error") else "error"
    
    # Create reasoning summary (not full trace)
    reasoning_summary = f"{len(state.get('reasoning_trace', []))} steps completed"
    
    return ScriptResponse(
        request_id=state["request_id"],
        status=status,
        script=state.get("script"),
        outline=state.get("outline"),
        char_count=state.get("char_count"),
        duration_target=state.get("duration"),
        reasoning_trace=reasoning_summary,
        iteration_count=state.get("iteration", 0),
        tokens_used_total=state.get("tokens_used", 0),
        retrieved_sources_count=state.get("retrieved_sources_count", 0),
        error_message=state.get("error"),
    )


# =============================================================================
# CLI FOR TESTING
# =============================================================================

if __name__ == "__main__":
    """Test Pydantic models and validation."""
    import json
    from datetime import datetime, timezone
    
    print("=" * 80)
    print("PYDANTIC MODELS VALIDATION TEST")
    print("=" * 80)
    
    # Test 1: Valid request
    print("\n1. Testing valid request:")
    print("-" * 80)
    
    valid_payload = {
        "isValid": True,
        "projectName": "AI Comedy Series",
        "genre": "Comedy",
        "storyIdea": "A programmer creates an AI that becomes self-aware and starts giving life advice",
        "duration": 5,
    }
    
    try:
        request = ScriptRequestItem(**valid_payload)
        print("  ✓ Request validated successfully")
        print(f"    - Project: {request.projectName}")
        print(f"    - Genre: {request.genre}")
        print(f"    - Duration: {request.duration} min")
        print(f"    - Request ID: {request.request_id} (auto-generated)")
    except Exception as e:
        print(f"  ✗ Validation failed: {e}")
    
    # Test 2: Request with explicit request_id
    print("\n2. Testing request with explicit request_id:")
    print("-" * 80)
    
    payload_with_id = {
        **valid_payload,
        "request_id": "custom-123-456"
    }
    
    try:
        request2 = ScriptRequestItem(**payload_with_id)
        print("  ✓ Request validated")
        print(f"    - Request ID: {request2.request_id} (provided)")
    except Exception as e:
        print(f"  ✗ Validation failed: {e}")
    
    # Test 3: Invalid requests
    print("\n3. Testing invalid requests:")
    print("-" * 80)
    
    invalid_cases = [
        (
            {**valid_payload, "isValid": False},  # Override after spread
            "isValid=False"
        ),
        (
            {**valid_payload, "duration": 0},
            "duration=0 (too short)"
        ),
        (
            {**valid_payload, "duration": 100},
            "duration=100 (too long)"
        ),
        (
            {**valid_payload, "storyIdea": ""},
            "empty storyIdea"
        ),
        (
            {**valid_payload, "projectName": ""},
            "empty projectName"
        ),
    ]
    
    for invalid_payload, description in invalid_cases:
        try:
            ScriptRequestItem(**invalid_payload)
            print(f"  ✗ Should have failed: {description}")
        except Exception as e:
            print(f"  ✓ Correctly rejected: {description}")
            print(f"      Error: {str(e)[:60]}...")
    
    # Test 4: Array format (n8n style)
    print("\n4. Testing array format (n8n style):")
    print("-" * 80)
    
    array_payload = [valid_payload]
    
    try:
        request_array = ScriptRequestArray(items=array_payload)
        first = request_array.first_item
        print("  ✓ Array validated")
        print(f"    - Array length: {len(request_array.items)}")
        print(f"    - First item genre: {first.genre}")
    except Exception as e:
        print(f"  ✗ Validation failed: {e}")
    
    # Test 5: Initial state creation
    print("\n5. Testing initial state creation:")
    print("-" * 80)
    
    try:
        request = ScriptRequestItem(**valid_payload)
        state = create_initial_state(request)
        
        print("  ✓ State created successfully")
        print(f"    - Request ID: {state['request_id']}")
        print(f"    - Language: {state['language']}")
        print(f"    - Target chars: {state['target_chars']:,}")
        print(f"    - Web search enabled: {state['web_search_enabled']}")
        print(f"    - Max iterations: {state['max_iterations']}")
    except Exception as e:
        print(f"  ✗ State creation failed: {e}")
    
    # Test 6: State to response conversion
    print("\n6. Testing state to response conversion:")
    print("-" * 80)
    
    try:
        # Simulate completed state
        completed_state = AgentState(
            request_id="test-123",
            project_name="Test Project",
            genre="Comedy",
            idea="Test idea",
            duration=5,
            language="en",
            target_chars=5000,
            outline="Test outline",
            script="Test script content",
            char_count=5100,
            tokens_used=2500,
            iteration=2,
            retrieved_sources_count=3,
            validation_passed=True,
            reasoning_trace=[
                ReasoningStep(
                    step=1,
                    action="retrieve",
                    result="success",
                    tokens_used=500,
                    timestamp=datetime.now(timezone.utc).isoformat()
                )
            ],
        )
        
        response = state_to_response(completed_state)
        print("  ✓ Response created successfully")
        print(f"    - Status: {response.status}")
        print(f"    - Script length: {len(response.script or '')} chars")
        print(f"    - Char count: {response.char_count}")
        print(f"    - Tokens used: {response.tokens_used_total}")
        print(f"    - Iterations: {response.iteration_count}")
        print(f"    - Reasoning: {response.reasoning_trace}")
        
        # Show JSON
        print("\n  Response JSON:")
        print(json.dumps(response.model_dump(), indent=4))
        
    except Exception as e:
        print(f"  ✗ Response creation failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 7: Russian language detection
    print("\n7. Testing Russian language detection:")
    print("-" * 80)
    
    russian_payload = {
        "isValid": True,
        "projectName": "Комедийный сериал",
        "genre": "Комедия",
        "storyIdea": "История о программисте, который создал ИИ",
        "duration": 7,
    }
    
    try:
        ru_request = ScriptRequestItem(**russian_payload)
        ru_state = create_initial_state(ru_request)
        
        print("  ✓ Russian request processed")
        print(f"    - Detected language: {ru_state['language']}")
        print(f"    - Target chars: {ru_state['target_chars']:,} (1450 chars/min)")
        print(f"    - Expected: {7 * 1450} chars")
        
    except Exception as e:
        print(f"  ✗ Failed: {e}")
    
    print("\n" + "=" * 80)
    print("✓ MODELS VALIDATION TEST COMPLETE")
    print("=" * 80)

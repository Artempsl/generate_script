"""
Test new response models (SegmentObject, SegmentedScriptResponse).

Validates:
- SegmentObject Pydantic validation
- SegmentedScriptResponse structure
- state_to_segmented_response() conversion
"""

import sys
from pathlib import Path
from uuid import uuid4

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.models import (
    SegmentObject,
    SegmentedScriptResponse,
    state_to_segmented_response,
    AgentState
)


def test_segment_object():
    """Test SegmentObject validation."""
    print("=" * 80)
    print("SEGMENT OBJECT TEST")
    print("=" * 80)
    
    # Test valid segment
    print("\n1. Testing valid SegmentObject...")
    try:
        segment = SegmentObject(
            segment_index=1,
            text="Detective Sarah sat in her office, reviewing case files.",
            audio_url="https://test.com/audio/test/0001.mp3"
        )
        print("   ✓ Valid segment created")
        print(f"     - Index: {segment.segment_index}")
        print(f"     - Text length: {len(segment.text)} chars")
        print(f"     - Audio URL: {segment.audio_url}")
    except Exception as e:
        print(f"   ✗ Validation failed: {e}")
        return False
    
    # Test invalid segment (index < 1)
    print("\n2. Testing invalid segment (index < 1)...")
    try:
        segment = SegmentObject(
            segment_index=0,
            text="Test",
            audio_url="https://test.com/audio/test/0000.mp3"
        )
        print("   ✗ Should have failed validation!")
        return False
    except Exception as e:
        print(f"   ✓ Correctly rejected: {e}")
    
    # Test invalid segment (text too short)
    print("\n3. Testing invalid segment (text too short)...")
    try:
        segment = SegmentObject(
            segment_index=1,
            text="Short",
            audio_url="https://test.com/audio/test/0001.mp3"
        )
        print("   ✗ Should have failed validation!")
        return False
    except Exception as e:
        print(f"   ✓ Correctly rejected: {e}")
    
    print("\n✅ All SegmentObject tests passed")
    return True


def test_segmented_response():
    """Test SegmentedScriptResponse."""
    print("\n" + "=" * 80)
    print("SEGMENTED RESPONSE TEST")
    print("=" * 80)
    
    print("\n1. Creating test response...")
    
    segments = [
        SegmentObject(
            segment_index=1,
            text="Detective Sarah reviewed the case files in her cluttered office.",
            audio_url="https://tunnel.com/audio/test/0001.mp3"
        ),
        SegmentObject(
            segment_index=2,
            text="A cryptic message appeared on her phone from an unknown number.",
            audio_url="https://tunnel.com/audio/test/0002.mp3"
        ),
        SegmentObject(
            segment_index=3,
            text="She realized Mark, her trusted partner, was the killer all along.",
            audio_url="https://tunnel.com/audio/test/0003.mp3"
        )
    ]
    
    response = SegmentedScriptResponse(
        request_id=str(uuid4()),
        status="success",
        project_name="Test Project",
        segments=segments,
        char_count=1050,
        duration_target=1,
        iteration_count=1,
        tokens_used_total=15000,
        retrieved_sources_count=5,
        reasoning_trace="8 steps completed"
    )
    
    print("   ✓ Response created")
    print(f"     - Status: {response.status}")
    print(f"     - Project: {response.project_name}")
    print(f"     - Segments: {len(response.segments)}")
    print(f"     - Char count: {response.char_count}")
    
    # Test JSON serialization
    print("\n2. Testing JSON serialization...")
    try:
        json_data = response.model_dump()
        print("   ✓ JSON serialization successful")
        print(f"     - Keys: {list(json_data.keys())}")
        assert "segments" in json_data
        assert len(json_data["segments"]) == 3
        print(f"     - Segments in JSON: {len(json_data['segments'])}")
    except Exception as e:
        print(f"   ✗ JSON serialization failed: {e}")
        return False
    
    print("\n✅ All SegmentedScriptResponse tests passed")
    return True


def test_state_conversion():
    """Test state_to_segmented_response() conversion."""
    print("\n" + "=" * 80)
    print("STATE CONVERSION TEST")
    print("=" * 80)
    
    print("\n1. Creating test state...")
    
    # Simulate final AgentState after full pipeline
    test_state: AgentState = {
        "request_id": str(uuid4()),
        "project_name": "Test Conversion",
        "genre": "Thriller",
        "idea": "A detective mystery",
        "duration": 1,
        "language": "en",
        "target_chars": 1000,
        "retrieved_context": "...",
        "web_context": "",
        "synthesized_context": "...",
        "retrieved_sources_count": 5,
        "reasoning": "Full reasoning...",
        "reasoning_strategy": {},
        "outline": "Test outline",
        "script": "Full script text...",
        "char_count": 1050,
        "validation_passed": True,
        "validation_ratio": 1.05,
        "validation_message": "Valid",
        "iteration": 0,
        "max_iterations": 3,
        "web_search_enabled": False,
        "should_regenerate": False,
        "reasoning_trace": [
            {"step": 1, "action": "retrieve", "result": "success", "tokens_used": 500, "timestamp": "2026-03-05T10:00:00Z"}
        ],
        "tokens_used": 15000,
        "error": None,
        "segments": [
            {
                "segment_index": 1,
                "text": "Detective Sarah sat in her cluttered office.",
                "audio_url": "https://tunnel.com/audio/test/0001.mp3"
            },
            {
                "segment_index": 2,
                "text": "Her phone buzzed with a cryptic message.",
                "audio_url": "https://tunnel.com/audio/test/0002.mp3"
            }
        ],
        "segment_count": 2,
        "audio_files": ["/audio/test/0001.mp3", "/audio/test/0002.mp3"],
        "audio_base_url": "https://tunnel.com",
        "audio_files_count": 2
    }
    
    print("   ✓ State created")
    
    # Convert to response
    print("\n2. Converting state to SegmentedScriptResponse...")
    try:
        response = state_to_segmented_response(test_state)
        print("   ✓ Conversion successful")
        print(f"     - Request ID: {response.request_id}")
        print(f"     - Status: {response.status}")
        print(f"     - Project: {response.project_name}")
        print(f"     - Segments: {len(response.segments)}")
        print(f"     - Tokens: {response.tokens_used_total}")
    except Exception as e:
        print(f"   ✗ Conversion failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Validate response structure
    print("\n3. Validating response structure...")
    assert response.status == "success"
    assert response.project_name == "Test Conversion"
    assert len(response.segments) == 2
    assert response.segments[0].segment_index == 1
    assert response.segments[1].segment_index == 2
    assert "tunnel.com" in response.segments[0].audio_url
    print("   ✓ All assertions passed")
    
    # Test JSON output
    print("\n4. Testing JSON output...")
    import json
    json_output = json.dumps(response.model_dump(), indent=2)
    print(json_output[:500] + "...")
    
    print("\n✅ All state conversion tests passed")
    return True


def main():
    """Run all response model tests."""
    results = []
    
    results.append(test_segment_object())
    results.append(test_segmented_response())
    results.append(test_state_conversion())
    
    print("\n" + "=" * 80)
    if all(results):
        print("✅ ALL RESPONSE MODEL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 80)


if __name__ == "__main__":
    main()

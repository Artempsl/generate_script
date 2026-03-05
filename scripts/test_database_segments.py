"""
Test database operations with new segments fields.

Validates:
- Execution class with segments and audio_files_count
- save_execution() with new fields
- get_execution() retrieves new fields correctly
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.database import DatabaseManager, Execution


async def test_segments_database():
    """Test database with new segments fields."""
    print("=" * 80)
    print("DATABASE SEGMENTS TEST")
    print("=" * 80)
    
    db_manager = DatabaseManager()
    
    # Initialize
    print("\n1. Initializing database...")
    await db_manager.initialize()
    print("   ✓ Database initialized")
    
    # Create test execution with segments
    print("\n2. Creating test execution with segments...")
    
    test_segments = [
        {
            "segment_index": 1,
            "text": "Detective Sarah sat in her office, case files sprawled across the desk.",
            "audio_url": "https://test.com/audio/test/0001.mp3"
        },
        {
            "segment_index": 2,
            "text": "Her phone buzzed with a cryptic message from the killer.",
            "audio_url": "https://test.com/audio/test/0002.mp3"
        },
        {
            "segment_index": 3,
            "text": "She realized the truth—Mark, her confidant, was the murderer.",
            "audio_url": "https://test.com/audio/test/0003.mp3"
        }
    ]
    
    test_execution = Execution(
        request_id="test-segments-001",
        status="success",
        project_name="Test Segments",
        genre="Thriller",
        duration=1,
        language="en",
        outline="Test outline",
        script="Full script text...",
        char_count=1050,
        target_chars=1000,
        iteration_count=1,
        tokens_used_total=15000,
        retrieved_sources_count=5,
        reasoning_trace=[
            {"step": 1, "action": "retrieve", "result": "success"},
            {"step": 2, "action": "segment", "result": f"{len(test_segments)} segments"},
            {"step": 3, "action": "generate_audio", "result": "3 audio files"}
        ],
        segments=test_segments,
        audio_files_count=3
    )
    
    print(f"   ✓ Execution created")
    print(f"     - Request ID: {test_execution.request_id}")
    print(f"     - Segments: {len(test_execution.segments)}")
    print(f"     - Audio files: {test_execution.audio_files_count}")
    
    # Save to database
    print("\n3. Saving to database...")
    await db_manager.save_execution(test_execution)
    print("   ✓ Execution saved")
    
    # Retrieve from database
    print("\n4. Retrieving from database...")
    retrieved = await db_manager.get_execution("test-segments-001")
    
    if not retrieved:
        print("   ✗ Execution not found!")
        return
    
    print("   ✓ Execution retrieved")
    print(f"     - Request ID: {retrieved.request_id}")
    print(f"     - Status: {retrieved.status}")
    print(f"     - Segments: {len(retrieved.segments)}")
    print(f"     - Audio files count: {retrieved.audio_files_count}")
    
    # Validate segments structure
    print("\n5. Validating segments structure...")
    for segment in retrieved.segments:
        assert "segment_index" in segment, "Missing segment_index"
        assert "text" in segment, "Missing text"
        assert "audio_url" in segment, "Missing audio_url"
        print(f"   ✓ Segment {segment['segment_index']}: {len(segment['text'])} chars")
    
    # Test to_response() format
    print("\n6. Testing to_response() format...")
    response = retrieved.to_response()
    print("   ✓ Response generated")
    print(f"     - request_id: {response['request_id']}")
    print(f"     - status: {response['status']}")
    print(f"     - segments count: {len(response.get('segments', []))}")
    
    # Display response structure
    print("\n7. Response structure:")
    import json
    print(json.dumps(response, indent=2))
    
    print("\n" + "=" * 80)
    print("✅ DATABASE SEGMENTS TEST PASSED")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_segments_database())

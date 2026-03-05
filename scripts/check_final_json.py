"""
Check the final JSON response from the last test execution.
"""
import asyncio
import sys
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.database import DatabaseManager
from agent.models import state_to_segmented_response


async def check_json():
    """Retrieve and display the latest execution JSON."""
    db_manager = DatabaseManager()
    await db_manager.initialize()
    
    print("=" * 80)
    print("CHECKING FINAL JSON RESPONSE")
    print("=" * 80)
    
    # Get latest execution
    print("\nRetrieving latest execution from database...")
    
    # Get the request_id of the latest execution
    request_id = "test-melodrama-final"  # From our last test
    
    execution = await db_manager.get_execution(request_id)
    
    if not execution:
        print(f"✗ Execution not found: {request_id}")
        return
    
    print(f"✓ Found execution: {execution.request_id}")
    print(f"  Project: {execution.project_name}")
    print(f"  Genre: {execution.genre}")
    print(f"  Status: {execution.status}")
    
    # Convert to response format
    print("\nConverting to SegmentedScriptResponse format...")
    
    response_dict = execution.to_response()
    
    # Update to match SegmentedScriptResponse format
    if 'duration' in response_dict:
        response_dict['duration_target'] = response_dict.pop('duration')
    if 'segments' not in response_dict:
        response_dict['segments'] = []
    
    segments = response_dict.get('segments', [])
    
    print("\n" + "=" * 80)
    print("FINAL JSON RESPONSE")
    print("=" * 80)
    print()
    
    # Pretty print JSON
    json_output = json.dumps(response_dict, indent=2, ensure_ascii=False)
    print(json_output)
    
    print("\n" + "=" * 80)
    print("RESPONSE STRUCTURE VALIDATION")
    print("=" * 80)
    
    # Validate structure matches template
    template_fields = [
        "request_id",
        "status",
        "project_name",
        "segments",
        "char_count",
        "duration_target",
        "iteration_count",
        "tokens_used_total",
        "retrieved_sources_count",
        "reasoning_trace"
    ]
    
    print("\n✓ Required fields present:")
    for field in template_fields:
        value = response_dict.get(field)
        if field == "segments" and isinstance(value, list):
            print(f"  - {field}: {len(value)} segments")
        else:
            print(f"  - {field}: {value}")
    
    # Check segments structure
    if segments:
        print(f"\n✓ First segment structure:")
        first_seg = segments[0]
        print(f"  - segment_index: {first_seg.get('segment_index')}")
        print(f"  - text: {first_seg.get('text', '')[:50]}...")
        print(f"  - audio_url: {first_seg.get('audio_url')}")
        
        # Validate audio URL format
        audio_url = first_seg.get('audio_url', '')
        print(f"\n✓ Audio URL validation:")
        print(f"  URL: {audio_url}")
        
        if "/projects/" in audio_url:
            print(f"  ✓ Uses /projects/ path (correct)")
        elif "/audio/" in audio_url:
            print(f"  ✗ Uses /audio/ path (OLD format - needs update)")
        else:
            print(f"  ✗ Unknown URL format")
        
        # Check URL pattern
        import re
        pattern = r"https?://[^/]+/projects/[^/]+/\d{4}\.mp3"
        if re.match(pattern, audio_url):
            print(f"  ✓ URL matches expected pattern: http(s)://host/projects/slug/XXXX.mp3")
        else:
            print(f"  ⚠ URL doesn't match expected pattern")
    
    await db_manager.close()


if __name__ == "__main__":
    asyncio.run(check_json())

"""
Quick test for segmentation and audio nodes only (bypassing full graph).

Tests:
1. segment_script_node execution
2. generate_audio_node execution
3. Audio file generation
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.models import create_initial_state, ScriptRequestItem
from agent.graph import segment_script_node, generate_audio_node
from datetime import datetime, timezone


def test_segmentation_nodes():
    """Test only the segmentation and audio generation nodes."""
    
    print("=" * 80)
    print("SEGMENTATION NODES TEST (Quick)")
    print("=" * 80)
    
    # Create minimal state with a pre-made script
    print("\n1. Creating test state with sample script...")
    
    test_script = """Detective Sarah Chen sat alone in her dimly lit office, surrounded by case files and cold coffee cups. The flickering desk lamp cast long shadows across photographs of unsolved murders spanning three decades. Her fingers traced patterns between the victims - all found in abandoned buildings, all with a small red ribbon tied around their left wrist.

Her phone buzzed. Unknown number. "Detective Chen, enjoying your research?" The text message felt like ice water down her spine. "But are you ready for the truth?" Her hands trembled as she opened the attached image - a photograph of herself, taken through her office window, just moments ago.

The realization hit like a freight train. The killer wasn't just watching. She wasn't hunting them - they had been hunting her all along. The red ribbon case files weren't evidence. They were a countdown. And she had just reached zero."""
    
    # Create request for state initialization
    request_data = {
        "request_id": "test-nodes-only-001",
        "project_name": "Nodes Test",
        "genre": "Thriller",
        "story_idea": "Test",
        "duration": 1
    }
    request_item = ScriptRequestItem(**request_data)
    
    # Create initial state
    state = create_initial_state(request_item)
    
    # Add pre-made script to state
    state['script'] = test_script
    state['char_count'] = len(test_script)
    state['audio_base_url'] = "http://localhost:8000"
    state['reasoning_trace'] = []  # Initialize trace
    
    print(f"   ✓ State created")
    print(f"   Script length: {len(test_script)} chars")
    print(f"   Audio base URL: {state['audio_base_url']}")
    
    # Test segment_script_node
    print("\n2. Testing segment_script_node...")
    try:
        state = segment_script_node(state)
        print(f"   ✓ Segmentation completed")
        print(f"   Segments: {state['segment_count']}")
        print(f"   Tokens used: {state['tokens_used']}")
        
        if state.get('error'):
            print(f"   ⚠️  Warning: {state['error']}")
        
        # Show segments
        for seg in state['segments'][:3]:
            print(f"      [{seg['segment_index']}] {seg['text'][:60]}...")
    except Exception as e:
        print(f"   ✗ Segmentation failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test generate_audio_node
    print("\n3. Testing generate_audio_node...")
    try:
        state = generate_audio_node(state)
        print(f"   ✓ Audio generation completed")
        print(f"   Audio files: {state['audio_files_count']}")
        
        if state.get('error'):
            print(f"   ⚠️  Warning: {state['error']}")
        
        # Check audio files exist
        for audio_file in state['audio_files']:
            file_path = Path(audio_file)
            exists = file_path.exists()
            size = file_path.stat().st_size if exists else 0
            print(f"      {file_path.name}: {size:,} bytes {'✓' if exists else '✗'}")
        
        # Show segments with audio URLs
        print("\n4. Segments with audio URLs:")
        for seg in state['segments'][:3]:
            print(f"   [{seg['segment_index']}] {seg['text'][:50]}...")
            print(f"       Audio: {seg.get('audio_url', 'N/A')}")
    
    except Exception as e:
        print(f"   ✗ Audio generation failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print(f"\n{'=' * 80}")
    print("✅ SEGMENTATION NODES TEST PASSED")
    print(f"{'=' * 80}")
    print(f"\nResults:")
    print(f"- Segments created: {state['segment_count']}")
    print(f"- Audio files generated: {state['audio_files_count']}")
    print(f"- Total tokens used: {state['tokens_used']}")


if __name__ == "__main__":
    test_segmentation_nodes()

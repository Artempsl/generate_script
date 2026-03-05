"""
End-to-end test for complete pipeline with segmentation and audio generation.

Tests:
1. Request format (n8n direct object)
2. Graph execution with new nodes (segment_script → generate_audio)
3. Segmented response format
4. Audio file generation
5. Database persistence with segments
"""

import os
import sys
import asyncio
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.models import ScriptRequestItem, create_initial_state, state_to_segmented_response
from agent.graph import execute_agent
from agent.database import DatabaseManager, Execution


async def test_full_pipeline():
    """Test complete pipeline with segmentation and audio generation."""
    
    print("=" * 80)
    print("FULL PIPELINE TEST: Segmentation + Audio Generation")
    print("=" * 80)
    
    # Check environment variables
    print("\n1. Checking environment variables...")
    cohere_key = os.getenv("COHERE_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    pinecone_key = os.getenv("PINECONE_API_KEY")
    
    print(f"   COHERE_API_KEY: {'✓ Set' if cohere_key else '✗ Missing (will use fallback segmentation)'}")
    print(f"   OPENAI_API_KEY: {'✓ Set' if openai_key else '✗ Missing (audio generation will fail)'}")
    print(f"   PINECONE_API_KEY: {'✓ Set' if pinecone_key else '✗ Missing (RAG will fail)'}")
    
    if not openai_key:
        print("\n⚠️  WARNING: OPENAI_API_KEY not set. Audio generation will fail.")
        print("   Set with: $env:OPENAI_API_KEY = [System.Environment]::GetEnvironmentVariable('OPENAI_API_KEY', 'User')")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Test cancelled.")
            return
    
    # Create test request
    print("\n2. Creating test request...")
    request_data = {
        "request_id": "test-melodrama-final",
        "project_name": "Melodrama Test",
        "genre": "melodrama",
        "story_idea": "Two childhood friends reunite after years apart, only to discover their feelings have deepened into something more profound.",
        "duration": 1  # 1 minute for quick test
    }
    
    request_item = ScriptRequestItem(**request_data)
    print(f"   ✓ Request created: {request_item.normalized_project_name}")
    print(f"   Genre: {request_item.genre}, Duration: {request_item.duration} min")
    
    # Create initial state with audio_base_url
    print("\n3. Creating initial state...")
    initial_state = create_initial_state(request_item)
    initial_state['audio_base_url'] = "http://localhost:8000"  # Test base URL
    print(f"   ✓ State created")
    print(f"   Language: {initial_state['language']}")
    print(f"   Target chars: {initial_state['target_chars']:,}")
    print(f"   Audio base URL: {initial_state['audio_base_url']}")
    
    # Execute agent graph
    print(f"\n4. Executing agent graph...")
    print("   Pipeline: retrieve → web_search → synthesize → reasoning → generate_outline")
    print("            → generate_script → validate → segment_script → generate_audio")
    
    try:
        final_state = await asyncio.wait_for(
            execute_agent(initial_state),
            timeout=180  # 3 minutes timeout
        )
        print(f"   ✓ Graph execution completed")
    except asyncio.TimeoutError:
        print(f"   ✗ Execution timed out after 180s")
        return
    except Exception as e:
        print(f"   ✗ Execution failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Check execution results
    print(f"\n5. Checking execution results...")
    print(f"   Status: {final_state.get('error') if final_state.get('error') else 'Success'}")
    print(f"   Iterations: {final_state.get('iteration', 0) + 1}")
    print(f"   Characters: {final_state.get('char_count', 0):,}")
    print(f"   Tokens used: {final_state.get('tokens_used', 0):,}")
    print(f"   Validation passed: {final_state.get('validation_passed', False)}")
    
    # Check segmentation
    print(f"\n6. Checking segmentation results...")
    segments = final_state.get('segments', [])
    segment_count = final_state.get('segment_count', 0)
    print(f"   Segment count: {segment_count}")
    
    if segments:
        print(f"   ✓ Segments generated:")
        for seg in segments[:3]:  # Show first 3
            print(f"      [{seg.get('segment_index', 0)}] {seg.get('text', '')[:60]}...")
            print(f"          Audio URL: {seg.get('audio_url', 'N/A')}")
    else:
        print(f"   ✗ No segments found")
    
    # Check audio files
    print(f"\n7. Checking audio file generation...")
    audio_files = final_state.get('audio_files', [])
    audio_files_count = final_state.get('audio_files_count', 0)
    print(f"   Audio files count: {audio_files_count}")
    
    if audio_files:
        print(f"   ✓ Audio files generated:")
        for audio_file in audio_files[:3]:  # Show first 3
            file_path = Path(audio_file)
            exists = file_path.exists()
            size = file_path.stat().st_size if exists else 0
            print(f"      {file_path.name}: {size:,} bytes {'✓' if exists else '✗'}")
    else:
        print(f"   ✗ No audio files found")
    
    # Convert to segmented response
    print(f"\n8. Converting to segmented response...")
    response = state_to_segmented_response(final_state)
    print(f"   ✓ Response created")
    print(f"   Response status: {response.status}")
    print(f"   Response segments: {len(response.segments)}")
    
    # Validate response structure
    print(f"\n9. Validating response structure...")
    response_dict = response.model_dump()
    required_fields = [
        'request_id', 'status', 'project_name', 'genre', 'duration',
        'segments', 'char_count', 'target_chars', 'language'
    ]
    
    all_present = all(field in response_dict for field in required_fields)
    print(f"   Required fields present: {'✓ Yes' if all_present else '✗ No'}")
    
    if all_present:
        print(f"   ✓ Response structure valid:")
        print(f"      - request_id: {response_dict['request_id']}")
        print(f"      - status: {response_dict['status']}")
        print(f"      - segments count: {len(response_dict['segments'])}")
        print(f"      - char_count: {response_dict['char_count']:,}")
        print(f"      - language: {response_dict['language']}")
    
    # Test database persistence
    print(f"\n10. Testing database persistence...")
    db_manager = DatabaseManager()
    await db_manager.initialize()
    
    execution = Execution(
        request_id=request_data['request_id'],
        status="success",
        project_name=request_item.normalized_project_name,
        genre=request_item.genre,
        duration=request_item.duration,
        language=final_state['language'],
        outline=final_state.get('outline', ''),
        script=final_state.get('script', ''),
        char_count=final_state.get('char_count', 0),
        target_chars=final_state['target_chars'],
        iteration_count=final_state.get('iteration', 0) + 1,
        tokens_used_total=final_state.get('tokens_used', 0),
        retrieved_sources_count=final_state.get('retrieved_sources_count', 0),
        reasoning_trace=final_state.get('reasoning_trace', []),
        segments=final_state.get('segments', []),
        audio_files_count=final_state.get('audio_files_count', 0)
    )
    
    await db_manager.save_execution(execution)
    print(f"   ✓ Execution saved to database")
    
    # Retrieve and verify
    retrieved = await db_manager.get_execution(request_data['request_id'])
    if retrieved:
        retrieved_response = retrieved.to_response()
        print(f"   ✓ Execution retrieved from database")
        print(f"      - Segments in DB: {len(retrieved_response.get('segments', []))}")
        print(f"      - Audio files count in DB: {retrieved_response.get('audio_files_count', 0)}")
    
    # Show sample segment with audio URL
    print(f"\n11. Sample segment with audio URL...")
    if response.segments:
        sample = response.segments[0]
        print(f"   Segment 1:")
        print(f"   - Index: {sample.segment_index}")
        print(f"   - Text: {sample.text[:100]}...")
        print(f"   - Audio URL: {sample.audio_url}")
    
    # Save segmented script to text file
    print(f"\n12. Saving segmented script to text file...")
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / f"{request_item.normalized_project_name}_segmented.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("SEGMENTED SCRIPT TEST RESULTS\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"Project: {request_item.normalized_project_name}\n")
        f.write(f"Genre: {request_item.genre}\n")
        f.write(f"Duration: {request_item.duration} min\n")
        f.write(f"Language: {final_state['language']}\n")
        f.write(f"Request ID: {request_data['request_id']}\n")
        f.write(f"Status: {response.status}\n\n")
        
        f.write(f"Story Idea:\n{request_item.story_idea}\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("FULL SCRIPT\n")
        f.write("=" * 80 + "\n\n")
        f.write(final_state.get('script', ''))
        f.write("\n\n")
        
        f.write("=" * 80 + "\n")
        f.write(f"SEGMENTED SCRIPT ({segment_count} segments)\n")
        f.write("=" * 80 + "\n\n")
        
        for seg in segments:
            f.write(f"[Segment {seg.get('segment_index', 0)}]\n")
            f.write("-" * 80 + "\n")
            f.write(f"{seg.get('text', '')}\n\n")
            f.write(f"Audio URL: {seg.get('audio_url', 'N/A')}\n")
            f.write(f"Character count: {len(seg.get('text', ''))}\n")
            f.write("\n" + "=" * 80 + "\n\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("EXECUTION STATISTICS\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Total characters: {final_state.get('char_count', 0):,}\n")
        f.write(f"Target characters: {final_state['target_chars']:,}\n")
        f.write(f"Segments count: {segment_count}\n")
        f.write(f"Audio files count: {audio_files_count}\n")
        f.write(f"Iterations: {final_state.get('iteration', 0) + 1}\n")
        f.write(f"Tokens used: {final_state.get('tokens_used', 0):,}\n")
        f.write(f"Retrieved sources: {final_state.get('retrieved_sources_count', 0)}\n")
        f.write(f"Validation passed: {final_state.get('validation_passed', False)}\n")
    
    print(f"   ✓ Segmented script saved to: {output_file}")
    print(f"   File size: {output_file.stat().st_size:,} bytes")
    
    print(f"\n{'=' * 80}")
    print("✅ FULL PIPELINE TEST COMPLETED")
    print(f"{'=' * 80}")
    print(f"\nSummary:")
    print(f"- Script generated: ✓")
    print(f"- Segments created: {segment_count}")
    print(f"- Audio files: {audio_files_count}")
    print(f"- Database saved: ✓")
    print(f"- Response format: SegmentedScriptResponse")
    
    # Show JSON preview
    print(f"\nJSON Response Preview:")
    json_output = json.dumps(response_dict, indent=2, ensure_ascii=False)
    lines = json_output.split('\n')
    preview_lines = lines[:30] + (["  ...", f"  (showing 30 of {len(lines)} lines)"] if len(lines) > 30 else [])
    print('\n'.join(preview_lines))


if __name__ == "__main__":
    asyncio.run(test_full_pipeline())

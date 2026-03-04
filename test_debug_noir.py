"""Debug test for Noir Detective with detailed error tracking"""
import asyncio
import sys
import os
import traceback
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.api import generate_script
from agent.models import ScriptRequestItem, ScriptRequestArray

async def test_noir_debug():
    print("=" * 80)
    print("NOIR DETECTIVE DEBUG TEST")
    print("=" * 80)
    print(f"Start time: {datetime.now(timezone.utc).strftime('%H:%M:%S')}")
    print()
    
    try:
        # Create request
        print("→ Step 1: Creating ScriptRequestItem...")
        request_item = ScriptRequestItem(
            isValid=True,
            projectName="Noir Debug Test",
            genre="Noir Detective",
            storyIdea="Detective finds old photograph showing dead woman in crowd",
            duration=1,
            request_id=f"test-noir-debug-{int(datetime.now(timezone.utc).timestamp())}"
        )
        print(f"  ✓ Request ID: {request_item.request_id}")
        print(f"  ✓ Genre: {request_item.genre}")
        print(f"  ✓ Duration: {request_item.duration} min")
        
        # Wrap in array
        print("\n→ Step 2: Creating ScriptRequestArray...")
        request_array = ScriptRequestArray(items=[request_item])
        print("  ✓ Array created")
        
        # Call API
        print("\n→ Step 3: Calling generate_script API...")
        print("  (This will take 30-60 seconds...)")
        result = await generate_script(request_array)
        
        # Check result
        print("\n" + "=" * 80)
        print("✓ TEST COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print(f"Status: {result.get('status')}")
        print(f"Language: {result.get('language')}")
        print(f"Script length: {result.get('char_count')} characters")
        print(f"Target: {result.get('target_chars')} characters")
        print(f"Iterations: {result.get('iteration_count')}")
        print(f"Tokens used: {result.get('tokens_used_total')}")
        print(f"Sources: {result.get('retrieved_sources_count')}")
        
        # Check for errors
        if result.get('error'):
            print(f"\n⚠ WARNING: Error in result: {result['error']}")
        
        # Save script
        if result.get('script'):
            timestamp = request_item.request_id.split('-')[-1]
            filename = f"generated_script_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"PROJECT: {request_item.projectName}\n")
                f.write(f"GENRE: {request_item.genre}\n")
                f.write(f"DURATION: {request_item.duration} min\n")
                f.write(f"LANGUAGE: {result.get('language')}\n")
                f.write(f"LENGTH: {result.get('char_count')} characters\n")
                f.write(f"ITERATIONS: {result.get('iteration_count')}\n")
                f.write(f"TOKENS USED: {result.get('tokens_used_total')}\n")
                f.write(f"SOURCES: {result.get('retrieved_sources_count')} from Pinecone\n")
                f.write(f"GENERATED: {datetime.now(timezone.utc).isoformat()}\n")
                f.write("\n" + "=" * 70 + "\n\n")
                f.write(result['script'])
            
            print(f"\n✓ Script saved to: {filename}")
        else:
            print("\n✗ No script in result!")
        
        return result
        
    except Exception as e:
        print("\n" + "=" * 80)
        print("✗ TEST FAILED")
        print("=" * 80)
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("\nFull traceback:")
        print("-" * 80)
        traceback.print_exc()
        print("-" * 80)
        return None

if __name__ == "__main__":
    print(f"\nPython version: {sys.version}")
    print(f"Working directory: {os.getcwd()}\n")
    
    result = asyncio.run(test_noir_debug())
    
    if result:
        print("\n" + "=" * 80)
        print("SUCCESS: Test completed without errors")
        print("=" * 80)
        sys.exit(0)
    else:
        print("\n" + "=" * 80)
        print("FAILED: Test encountered errors (see above)")
        print("=" * 80)
        sys.exit(1)

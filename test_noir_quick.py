"""Quick Noir Detective Test (1 minute)"""
import asyncio
import sys
import os
from datetime import datetime, timezone

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.api import generate_script
from agent.models import ScriptRequestItem, ScriptRequestArray

async def test_noir():
    request_item = ScriptRequestItem(
        isValid=True,
        projectName="Noir Detective Quick Test",
        genre="Noir Detective",
        storyIdea="Private detective finds photograph of woman who died 10 years ago standing in yesterday's crowd",
        duration=1,  # 1 minute for speed
        request_id=f"test-noir-quick-{int(datetime.now(timezone.utc).timestamp())}"
    )
    
    # Wrap in array (API expects ScriptRequestArray)
    request_array = ScriptRequestArray(items=[request_item])
    
    print("=" * 80)
    print(f"NOIR DETECTIVE TEST (1 MINUTE)")
    print("=" * 80)
    print(f"Request ID: {request_item.request_id}")
    print(f"Genre: {request_item.genre}")
    print(f"Duration: {request_item.duration} minute")
    print()
    
    try:
        result = await generate_script(request_array)
        
        print("\n" + "=" * 80)
        print("✓ TEST COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print(f"Status: {result.get('status')}")
        print(f"Script length: {result.get('char_count')} characters")
        print(f"Iterations: {result.get('iteration_count')}")
        print(f"Tokens: {result.get('tokens_used_total')}")
        
        # Save to file
        if result.get('script'):
            filename = f"generated_script_{request_item.request_id.split('-')[-1]}.txt"
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
        
        return result
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(test_noir())

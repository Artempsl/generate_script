"""Quick test on Science Fiction to verify system works"""
import asyncio
import sys
import os
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.api import generate_script
from agent.models import ScriptRequestItem, ScriptRequestArray

async def test_scifi():
    print("=" * 80)
    print("SCIENCE FICTION TEST (1 MINUTE)")
    print("=" * 80)
    print(f"Start: {datetime.now(timezone.utc).strftime('%H:%M:%S')}\n")
    
    request_item = ScriptRequestItem(
        isValid=True,
        projectName="SciFi System Test",
        genre="Science Fiction",
        storyIdea="Robot discovers it has emotions after watching sunset",
        duration=1,
        request_id=f"test-scifi-{int(datetime.now(timezone.utc).timestamp())}"
    )
    
    request_array = ScriptRequestArray(items=[request_item])
    
    print(f"Request ID: {request_item.request_id}")
    print(f"Genre: {request_item.genre}\n")
    
    try:
        result = await generate_script(request_array)
        
        print("\n" + "=" * 80)
        print("✓ SUCCESS")
        print("=" * 80)
        print(f"Characters: {result.get('char_count')}")
        print(f"Iterations: {result.get('iteration_count')}")
        print(f"Tokens: {result.get('tokens_used_total')}")
        
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
                f.write(f"TOKENS: {result.get('tokens_used_total')}\n")
                f.write(f"GENERATED: {datetime.now(timezone.utc).isoformat()}\n")
                f.write("\n" + "=" * 70 + "\n\n")
                f.write(result['script'])
            print(f"✓ Saved: {filename}")
        
        return True
    except Exception as e:
        print(f"\n✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_scifi())
    sys.exit(0 if success else 1)

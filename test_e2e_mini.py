"""
Single E2E Test - Minimal script generation.
"""

import asyncio
import json
import httpx


async def test_mini_generation():
    """Test minimal script generation (2 min to save tokens)."""
    print("=" * 80)
    print("E2E TEST: Minimal Script Generation")
    print("=" * 80)
    
    request = {
        "items": [{
            "isValid": True,
            "projectName": "Mini Test",
            "genre": "Comedy",
            "storyIdea": "A robot learns to tell jokes.",
            "duration": 2,  # Minimal duration
            "request_id": "e2e-mini-001"
        }]
    }
    
    async with httpx.AsyncClient() as client:
        print(f"\n→ Sending request (2-min comedy)...")
        print(f"  Request ID: {request['items'][0]['request_id']}")
        
        try:
            response = await client.post(
                "http://localhost:8001/generate-script",
                json=request,
                timeout=120  # 2 minutes max
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"\n✓ SUCCESS!")
                print(f"  Status: {data['status']}")
                print(f"  Request ID: {data['request_id']}")
                print(f"  Iterations: {data.get('iteration_count', 0)}")
                print(f"  Tokens: {data.get('tokens_used_total', 0):,}")
                print(f"  Sources: {data.get('retrieved_sources_count', 0)}")
                print(f"  Char count: {data.get('char_count', 0):,}")
                print(f"  Target: {data.get('duration_target', 0) * 1000:,}")
                
                # Check script exists
                if data.get('script'):
                    script_preview = data['script'][:200] + "..."
                    print(f"\n  Script preview:")
                    print(f"  {script_preview}")
                    
                    # Save to file
                    with open("e2e_result.json", "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    print(f"\n  Full response saved to: e2e_result.json")
                
                print("\n" + "=" * 80)
                print("✓ E2E TEST PASSED")
                print("=" * 80)
                return True
            else:
                print(f"\n✗ FAILED: Status {response.status_code}")
                print(f"  Response: {response.text[:500]}")
                return False
                
        except asyncio.TimeoutError:
            print(f"\n✗ TIMEOUT: Request took > 120s")
            return False
        except Exception as e:
            print(f"\n✗ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    success = asyncio.run(test_mini_generation())
    exit(0 if success else 1)

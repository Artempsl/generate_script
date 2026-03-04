"""Test ReAct reasoning node with simple Horror script."""
import os
import time
import httpx
import asyncio

async def test_react_reasoning():
    # Test data
    request_data = {
        "items": [{
            "isValid": True,
            "projectName": "ReAct Test",
            "genre": "Thriller",
            "storyIdea": "A detective realizes the killer is someone they've been talking to all along",
            "duration": 1,
            "request_id": f"test-react-{int(time.time())}"
        }]
    }
    
    print("=" * 70)
    print("REACT REASONING TEST")
    print("=" * 70)
    print(f"Genre: {request_data['items'][0]['genre']}")
    print(f"Duration: {request_data['items'][0]['duration']} min")
    print(f"Idea: {request_data['items'][0]['storyIdea']}")
    print(f"Request ID: {request_data['items'][0]['request_id']}")
    print("=" * 70)
    print("\nSending request to server (with ReAct reasoning node)...")
    
    start_time = time.time()
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.post(
            "http://127.0.0.1:8001/generate-script",
            json=request_data
        )
    
    elapsed = time.time() - start_time
    
    print(f"\nResponse received in {elapsed:.2f}s")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        
        print("\n" + "=" * 70)
        print("GENERATION RESULT")
        print("=" * 70)
        print(f"Status: {result['results'][0]['status']}")
        print(f"Characters: {result['results'][0]['char_count']}")
        print(f"Target: {result['results'][0]['target_chars']}")
        print(f"Ratio: {result['results'][0]['char_count'] / result['results'][0]['target_chars']:.2%}")
        print(f"Iterations: {result['results'][0]['iteration_count']}")
        print(f"Tokens used: {result['results'][0]['tokens_used_total']}")
        print(f"Sources: {result['results'][0]['retrieved_sources_count']}")
        
        script = result['results'][0]['script']
        
        # Save to file
        request_id = request_data['items'][0]['request_id']
        filename = f"generated_script_{request_id.split('-')[-1]}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"PROJECT: {result['results'][0]['project_name']}\n")
            f.write(f"GENRE: {result['results'][0]['genre']}\n")
            f.write(f"DURATION: {result['results'][0]['duration']} min\n")
            f.write(f"LANGUAGE: {result['results'][0]['language']}\n")
            f.write(f"LENGTH: {result['results'][0]['char_count']} characters\n")
            f.write(f"ITERATIONS: {result['results'][0]['iteration_count']}\n")
            f.write(f"TOKENS USED: {result['results'][0]['tokens_used_total']}\n")
            f.write(f"GENERATED: {result['results'][0]['created_at']}\n")
            f.write(f"\n{'=' * 70}\n\n")
            f.write(script)
        
        print(f"\n✓ Script saved to: {filename}")
        
        # Show preview
        print(f"\n" + "=" * 70)
        print("SCRIPT PREVIEW (first 800 chars)")
        print("=" * 70)
        print(script[:800])
        if len(script) > 800:
            print("\n[... script continues ...]")
        
        print("\n" + "=" * 70)
        print("🧠 ReAct REASONING CHECK:")
        print("=" * 70)
        print("Check database for reasoning_trace to see ReAct thinking step!")
        print("Run: python show_reasoning.py")
        
        return True
    else:
        print(f"\n❌ Error: {response.text}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_react_reasoning())
    exit(0 if success else 1)

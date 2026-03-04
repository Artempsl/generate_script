"""
Final integration test - 1-minute comedy script via FastAPI.
"""
import requests
import time
import json

BASE_URL = "http://localhost:8001"

print("=" * 70)
print("FINAL INTEGRATION TEST - Stage 6 Complete")
print("=" * 70)

# Test request
request = {
    "items": [{
        "isValid": True,
        "projectName": "Stage 6 Complete Test",
        "genre": "Comedy",
        "storyIdea": "A developer fixes a bug after trying only 2 solutions",
        "duration": 1,
        "request_id": f"stage6-{int(time.time())}"
    }]
}

print(f"\n📝 Request: 1-minute comedy script")
print(f"   ID: {request['items'][0]['request_id']}")
print(f"   Expected: 30-90 seconds\n")
print("-" * 70)

start = time.time()

try:
    response = requests.post(
        f"{BASE_URL}/generate-script",
        json=request,
        timeout=120
    )
    
    elapsed = time.time() - start
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"\n✅ SUCCESS in {elapsed:.1f} seconds!\n")
        print(f"Status: {data.get('status')}")
        print(f"Language: {data.get('language')}")
        print(f"Iterations: {data.get('iteration_count')}")
        print(f"Tokens: {data.get('total_tokens_used'):,}")
        print(f"Script length: {len(data.get('script', ''))} chars")
        print(f"Validation: {data.get('validation_message', 'N/A')}")
        
        # Display script preview
        script = data.get('script', '')
        if script:
            lines = script.split('\n')
            print(f"\n📜 Script preview (first 10 lines):")
            print("-" * 70)
            for line in lines[:10]:
                print(line)
            if len(lines) > 10:
                print(f"... ({len(lines) - 10} more lines)")
        
        # Save result
        filename = f"stage6_success_{int(time.time())}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Full result saved to: {filename}")
        
        print("\n" + "=" * 70)
        print("🎉 STAGE 6: SERVER & INTEGRATION TESTING - COMPLETE!")
        print("=" * 70)
        
    else:
        print(f"\n❌ HTTP {response.status_code}")
        print(response.text)
        
except requests.Timeout:
    print(f"\n⏱️ TIMEOUT after {time.time() - start:.1f}s")
except Exception as e:
    print(f"\n❌ ERROR: {e}")

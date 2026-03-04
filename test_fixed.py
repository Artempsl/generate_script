"""
Simple E2E test after fixing event loop blocking issue.
"""
import requests
import time

BASE_URL = "http://localhost:8001"

print("=" * 60)
print("SIMPLE E2E TEST (After asyncio.to_thread fix)")
print("=" * 60)

# Test request
request = {
    "items": [{
        "isValid": True,
        "projectName": "Event Loop Test",
        "genre": "Comedy",
        "storyIdea": "A programmer discovers event loops exist in real life too",
        "duration": 2,
        "request_id": f"fix-test-{int(time.time())}"
    }]
}

print("\nSending request for 2-minute comedy script...")
print(f"Request ID: {request['items'][0]['request_id']}")
print("\nExpected time: 30-120 seconds")
print("=" * 60)

start = time.time()

try:
    response = requests.post(
        f"{BASE_URL}/generate-script",
        json=request,
        timeout=180
    )
    
    elapsed = time.time() - start
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ SUCCESS in {elapsed:.1f}s")
        print(f"\nRequest ID: {data.get('request_id')}")
        print(f"Status: {data.get('status')}")
        print(f"Language: {data.get('language')}")
        print(f"Script length: {len(data.get('script', ''))} chars")
        print(f"Iterations: {data.get('iteration_count')}")
        print(f"Tokens used: {data.get('total_tokens_used')}")
        
        # Save result
        filename = f"test_fixed_{int(time.time())}.json"
        import json
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Saved to: {filename}")
        
    else:
        print(f"\n❌ FAILED with status {response.status_code}")
        print(response.text)
        
except requests.Timeout:
    elapsed = time.time() - start
    print(f"\n⏱️ TIMEOUT after {elapsed:.1f}s")
except Exception as e:
    elapsed = time.time() - start
    print(f"\n❌ ERROR after {elapsed:.1f}s: {e}")

print("\n" + "=" * 60)

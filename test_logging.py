"""
Quick test with detailed logging - very short 1-minute script.
"""
import requests
import time

BASE_URL = "http://localhost:8001"

request = {
    "items": [{
        "isValid": True,
        "projectName": "Quick Logging Test",
        "genre": "Comedy",
        "storyIdea": "Simple test",
        "duration": 1,
        "request_id": f"log-test-{int(time.time())}"
    }]
}

print(f"Testing with logging... (1-min script)")
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
        print(f"\n✅ SUCCESS in {elapsed:.1f}s")
        print(f"Status: {data.get('status')}")
        print(f"Script length: {len(data.get('script', ''))} chars")
    else:
        print(f"\n❌ FAILED: {response.status_code}")
        
except requests.Timeout:
    print(f"\n⏱️ TIMEOUT after {time.time() - start:.1f}s")
except Exception as e:
    print(f"\n❌ ERROR: {e}")

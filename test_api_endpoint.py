"""Ultra-simple sync test via FastAPI endpoint"""
import requests
import json
from datetime import datetime, timezone

API_URL = "http://localhost:8000/generate-script"

def test_via_api():
    print("=" * 80)
    print("API ENDPOINT TEST")
    print("=" * 80)
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}\n")
    
    request_data = {
        "items": [{
            "isValid": True,
            "projectName": "API Test",
            "genre": "Action",
            "storyIdea": "Hero saves city from villain",
            "duration": 1,
            "request_id": f"test-api-{int(datetime.now(timezone.utc).timestamp())}"
        }]
    }
    
    print(f"Request ID: {request_data['items'][0]['request_id']}")
    print(f"Sending POST to {API_URL}...")
    print("(This will take 30-60 seconds...)\n")
    
    try:
        response = requests.post(
            API_URL,
            json=request_data,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            print("\n" + "=" * 80)
            print("✓ SUCCESS")
            print("=" * 80)
            print(f"Status: {result.get('status')}")
            print(f"Characters: {result.get('char_count')}")
            print(f"Tokens: {result.get('tokens_used_total')}")
            print(f"Iterations: {result.get('iteration_count')}")
            return True
        else:
            print(f"\n✗ FAILED: HTTP {response.status_code}")
            print(response.text)
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: API server not running!")
        print("Start server with: uvicorn agent.api:app --reload")
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_via_api()
    exit(0 if success else 1)

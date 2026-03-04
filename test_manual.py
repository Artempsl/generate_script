"""
Manual E2E Test - 2-minute script generation.
Run with server already started.
"""

import requests
import json
import time


BASE_URL = "http://localhost:8001"


def test_2min_script():
    """Test 2-minute script generation."""
    print("=" * 80)
    print("MANUAL E2E TEST: 2-Minute Script Generation")
    print("=" * 80)
    
    # Test request
    request = {
        "items": [{
            "isValid": True,
            "projectName": "Quick Comedy Test",
            "genre": "Comedy",
            "storyIdea": "A robot learns to make coffee but keeps adding too much sugar, creating chaos in the office.",
            "duration": 2,
            "request_id": f"manual-test-{int(time.time())}"
        }]
    }
    
    print(f"\nRequest:")
    print(f"  Duration: {request['items'][0]['duration']} minutes")
    print(f"  Genre: {request['items'][0]['genre']}")
    print(f"  Request ID: {request['items'][0]['request_id']}")
    print(f"\nSending request to {BASE_URL}/generate-script...")
    print("This will take 30-120 seconds...\n")
    
    start = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/generate-script",
            json=request,
            timeout=180
        )
        
        duration = time.time() - start
        
        print(f"Response received in {duration:.1f}s")
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n" + "=" * 80)
            print("SUCCESS!")
            print("=" * 80)
            print(f"Status: {data['status']}")
            print(f"Request ID: {data['request_id']}")
            print(f"Iterations: {data.get('iteration_count', 0)}")
            print(f"Tokens used: {data.get('tokens_used_total', 0):,}")
            print(f"Sources retrieved: {data.get('retrieved_sources_count', 0)}")
            print(f"Character count: {data.get('char_count', 0):,}")
            print(f"Target chars: ~{data.get('duration_target', 0) * 1000:,}")
            
            if data.get('script'):
                print(f"\nScript length: {len(data['script']):,} characters")
                print(f"\nScript preview (first 300 chars):")
                print("-" * 80)
                print(data['script'][:300] + "...")
                print("-" * 80)
                
                # Save full response
                filename = f"manual_test_{request['items'][0]['request_id']}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"\nFull response saved to: {filename}")
            
            if data.get('outline'):
                print(f"\nOutline preview (first 200 chars):")
                print(data['outline'][:200] + "...")
            
            print("\n" + "=" * 80)
            return True
        else:
            print(f"\nFAILED: {response.status_code}")
            print(response.text[:500])
            return False
            
    except requests.Timeout:
        print(f"\nTIMEOUT after {time.time() - start:.1f}s")
        return False
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("ERROR: Server not healthy")
            print("Please start server first: python server.py")
            exit(1)
    except:
        print("ERROR: Server not running")
        print("Please start server first: python server.py")
        exit(1)
    
    # Run test
    success = test_2min_script()
    exit(0 if success else 1)

"""
Test new n8n array format for /generate-script endpoint.

This test verifies that the API correctly accepts direct array format:
[
  {
    "isValid": true,
    "projectName": "...",
    "genre": "...",
    "storyIdea": "...",
    "duration": 1
  }
]
"""

import requests
import json
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000/generate-script"

# Test data - direct array format (as n8n sends)
test_data = [
    {
        "isValid": True,
        "projectName": "n8n Format Test",
        "genre": "Sci-Fi",
        "storyIdea": "A scientist discovers time travel but realizes every change creates a darker timeline",
        "duration": 1
    }
]

print("=" * 80)
print("N8N ARRAY FORMAT TEST")
print("=" * 80)
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"API URL: {API_URL}")
print(f"\nRequest Body (n8n format):")
print(json.dumps(test_data, indent=2))

# Make request
print("\n" + "→" * 40)
print("Sending POST request...")

try:
    response = requests.post(
        API_URL,
        json=test_data,  # Send direct array
        headers={"Content-Type": "application/json"},
        timeout=360  # 6 minutes
    )
    
    print(f"← Response Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        print("\n" + "=" * 80)
        print("✓ TEST PASSED - API ACCEPTS N8N FORMAT")
        print("=" * 80)
        
        print(f"\nRequest ID: {data.get('request_id')}")
        print(f"Status: {data.get('status')}")
        print(f"Project: {data.get('project_name')}")
        print(f"Genre: {data.get('genre')}")
        print(f"Language: {data.get('language')}")
        print(f"Duration: {data.get('duration')} min")
        
        print(f"\n📊 Metrics:")
        print(f"  Characters: {data.get('char_count')} / {data.get('target_chars')} target")
        print(f"  Iterations: {data.get('iteration_count')}")
        print(f"  Tokens Used: {data.get('tokens_used_total'):,}")
        print(f"  Sources: {data.get('retrieved_sources_count')}")
        print(f"  Validation: {'✓ Passed' if data.get('validation_passed') else '✗ Failed'}")
        
        # Script preview
        script = data.get('script', '')
        print(f"\n📝 Script Preview ({len(script)} chars):")
        print("─" * 80)
        print(script[:300] + "..." if len(script) > 300 else script)
        print("─" * 80)
        
        # Outline preview
        outline = data.get('outline', '')
        if outline:
            print(f"\n📋 Outline Preview ({len(outline)} chars):")
            print("─" * 80)
            print(outline[:200] + "..." if len(outline) > 200 else outline)
            print("─" * 80)
        
        print(f"\n✓ Script saved with ID: {data.get('request_id')}")
        print(f"✓ Timestamp: {data.get('created_at')}")
        
    elif response.status_code == 422:
        print("\n" + "=" * 80)
        print("✗ VALIDATION ERROR")
        print("=" * 80)
        print(json.dumps(response.json(), indent=2))
        
    elif response.status_code == 500:
        print("\n" + "=" * 80)
        print("✗ SERVER ERROR")
        print("=" * 80)
        error = response.json()
        print(f"Error: {error.get('detail')}")
        
    else:
        print("\n" + "=" * 80)
        print(f"✗ UNEXPECTED STATUS: {response.status_code}")
        print("=" * 80)
        print(response.text)

except requests.exceptions.ConnectionError:
    print("\n" + "=" * 80)
    print("✗ CONNECTION ERROR")
    print("=" * 80)
    print("FastAPI server is not running!")
    print("\nStart server with:")
    print("  python -m uvicorn agent.api:app --host 0.0.0.0 --port 8000")
    
except requests.exceptions.Timeout:
    print("\n" + "=" * 80)
    print("✗ TIMEOUT")
    print("=" * 80)
    print("Request took longer than 6 minutes")
    
except Exception as e:
    print("\n" + "=" * 80)
    print("✗ UNEXPECTED ERROR")
    print("=" * 80)
    print(f"Error: {str(e)}")

print("\n" + "=" * 80)

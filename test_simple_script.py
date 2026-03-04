"""
Simple script generation test - wait for completion.
"""
import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:8001"

print("=" * 70)
print(f"SCRIPT GENERATION TEST - {datetime.now().strftime('%H:%M:%S')}")
print("=" * 70)

request_data = {
    "items": [{
        "isValid": True,
        "projectName": "Simple Test",
        "genre": "Comedy",
        "storyIdea": "A cat discovers the internet",
        "duration": 1,
        "request_id": f"test-{int(time.time())}"
    }]
}

print(f"\n📝 Generating 1-minute comedy script...")
print(f"Request ID: {request_data['items'][0]['request_id']}")
print(f"\n⏳ Please wait (30-90 seconds)...\n")

start_time = time.time()

try:
    response = requests.post(
        f"{BASE_URL}/generate-script",
        json=request_data,
        timeout=120
    )
    
    elapsed = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"\n{'=' * 70}")
        print(f"✅ SUCCESS in {elapsed:.1f} seconds!")
        print(f"{'=' * 70}\n")
        
        print(f"📊 Statistics:")
        print(f"   Status: {result.get('status')}")
        print(f"   Language: {result.get('language')}")
        print(f"   Iterations: {result.get('iteration_count')}")
        print(f"   Tokens used: {result.get('total_tokens_used'):,}")
        print(f"   Validation: {result.get('validation_message')}")
        
        script = result.get('script', '')
        print(f"\n📜 Script ({len(script)} characters):")
        print("=" * 70)
        print(script)
        print("=" * 70)
        
        # Save to file
        filename = f"generated_script_{int(time.time())}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"PROJECT: {result.get('project_name')}\n")
            f.write(f"GENRE: {result.get('genre')}\n")
            f.write(f"DURATION: {result.get('duration')} min\n")
            f.write(f"LANGUAGE: {result.get('language')}\n")
            f.write(f"GENERATED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"\n{'=' * 70}\n\n")
            f.write(script)
        
        print(f"\n💾 Script saved to: {filename}")
        
        # Save full JSON
        json_filename = f"generated_script_{int(time.time())}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"💾 Full result saved to: {json_filename}")
        
        print(f"\n{'=' * 70}")
        print("🎉 TEST PASSED - Script generated successfully!")
        print(f"{'=' * 70}\n")
        
    else:
        print(f"\n❌ HTTP Error {response.status_code}")
        print(response.text)
        
except requests.Timeout:
    print(f"\n❌ TIMEOUT after {time.time() - start_time:.1f} seconds")
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

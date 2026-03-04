"""Final Noir Detective test via API"""
import requests
import json
from datetime import datetime, timezone

API_URL = "http://localhost:8000/generate-script"

def test_noir_via_api():
    print("=" * 80)
    print("NOIR DETECTIVE TEST (VIA API)")
    print("=" * 80)
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}\n")
    
    request_data = {
        "items": [{
            "isValid": True,
            "projectName": "Noir Detective Final Test",
            "genre": "Noir Detective",
            "storyIdea": "Private detective receives mysterious photograph of woman who died 10 years ago standing in yesterday's crowd",
            "duration": 1,
            "request_id": f"test-noir-final-{int(datetime.now(timezone.utc).timestamp())}"
        }]
    }
    
    print(f"Request ID: {request_data['items'][0]['request_id']}")
    print(f"Genre: Noir Detective")
    print(f"Duration: 1 minute\n")
    print("Sending request... (30-60 seconds)\n")
    
    try:
        response = requests.post(
            API_URL,
            json=request_data,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            print("\n" + "=" * 80)
            print("✓ NOIR DETECTIVE TEST SUCCESS!")
            print("=" * 80)
            print(f"Status: {result.get('status')}")
            print(f"Language: {result.get('language')}")
            print(f"Characters: {result.get('char_count')}")
            print(f"Target: {result.get('target_chars')}")
            print(f"Iterations: {result.get('iteration_count')}")
            print(f"Tokens: {result.get('tokens_used_total')}")
            print(f"Sources: {result.get('retrieved_sources_count')}")
            
            # Save script
            if result.get('script'):
                timestamp = request_data['items'][0]['request_id'].split('-')[-1]
                filename = f"generated_script_{timestamp}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"PROJECT: {request_data['items'][0]['projectName']}\n")
                    f.write(f"GENRE: {request_data['items'][0]['genre']}\n")
                    f.write(f"DURATION: {request_data['items'][0]['duration']} min\n")
                    f.write(f"LANGUAGE: {result.get('language')}\n")
                    f.write(f"LENGTH: {result.get('char_count')} characters\n")
                    f.write(f"ITERATIONS: {result.get('iteration_count')}\n")
                    f.write(f"TOKENS: {result.get('tokens_used_total')}\n")
                    f.write(f"SOURCES: {result.get('retrieved_sources_count')} from Pinecone\n")
                    f.write(f"GENERATED: {datetime.now(timezone.utc).isoformat()}\n")
                    f.write("\n" + "=" * 70 + "\n\n")
                    f.write(result['script'])
                print(f"\n✓ Script saved to: {filename}")
            
            print("\n" + "=" * 80)
            return True
        else:
            print(f"\n✗ FAILED: HTTP {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_noir_via_api()
    exit(0 if success else 1)

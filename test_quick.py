"""
Quick Integration Tests for Agent Backend.

Fast validation tests without full script generation.
"""

import asyncio
import httpx


BASE_URL = "http://localhost:8001"


async def test_all():
    """Run quick validation tests."""
    print("=" * 80)
    print("QUICK INTEGRATION TESTS")
    print("=" * 80)
    
    async with httpx.AsyncClient() as client:
        # Test 1: Root endpoint
        print("\n1. Testing root endpoint...")
        try:
            response = await client.get(f"{BASE_URL}/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✓ Service: {data['service']}")
                print(f"   ✓ Version: {data['version']}")
                print(f"   ✓ Status: {data['status']}")
            else:
                print(f"   ✗ Failed: {response.status_code}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        # Test 2: Health check
        print("\n2. Testing health endpoint...")
        try:
            response = await client.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✓ Status: {data['status']}")
                print(f"   ✓ Database: {data['database']['connected']}")
                print(f"   ✓ Executions: {data['database']['total_executions']}")
                env = data['environment']
                print(f"   ✓ OPENAI_API_KEY: {env['OPENAI_API_KEY']}")
                print(f"   ✓ PINECONE_API_KEY: {env['PINECONE_API_KEY']}")
                print(f"   ✓ COHERE_API_KEY: {env['COHERE_API_KEY']}")
            else:
                print(f"   ✗ Failed: {response.status_code}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        # Test 3: Test endpoint
        print("\n3. Testing /test endpoint...")
        try:
            response = await client.get(f"{BASE_URL}/test", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✓ Port: {data['config']['port']}")
                print(f"   ✓ Max iterations: {data['config']['max_iterations']}")
                print(f"   ✓ Max tokens: {data['config']['max_tokens']}")
            else:
                print(f"   ✗ Failed: {response.status_code}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        # Test 4: Statistics endpoint
        print("\n4. Testing /statistics endpoint...")
        try:
            response = await client.get(f"{BASE_URL}/statistics", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✓ Total executions: {data.get('total_executions', 0)}")
                print(f"   ✓ Success rate: {data.get('success_rate', 0):.1%}")
            else:
                print(f"   ✗ Failed: {response.status_code}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        # Test 5: Invalid request validation
        print("\n5. Testing request validation...")
        try:
            invalid_request = {
                "items": [{
                    "isValid": False,
                    "projectName": "Test",
                    "genre": "Test",
                    "storyIdea": "Test",
                    "duration": 5
                }]
            }
            response = await client.post(
                f"{BASE_URL}/generate-script",
                json=invalid_request,
                timeout=10
            )
            if response.status_code == 422:
                print(f"   ✓ Validation rejected (422)")
            else:
                print(f"   ✗ Unexpected: {response.status_code}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
    
    print("\n" + "=" * 80)
    print("✓ QUICK TESTS COMPLETE")
    print("=" * 80)
    print("\nNote: Full E2E test with script generation can be run separately")
    print("      using test_integration.py (takes 1-3 minutes)")


if __name__ == "__main__":
    asyncio.run(test_all())

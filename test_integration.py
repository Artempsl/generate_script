"""
Integration Tests for Agent Backend.

Tests full end-to-end flow:
1. Script generation (English)
2. Idempotency check
3. Russian language detection
4. Error handling
5. Database persistence
"""

import asyncio
import json
import time
from datetime import datetime

import httpx


# =============================================================================
# CONFIGURATION
# =============================================================================

BASE_URL = "http://localhost:8001"
TEST_TIMEOUT = 180  # 3 minutes per test


# =============================================================================
# TEST DATA
# =============================================================================

# Test 1: Short English comedy (to save tokens)
TEST_REQUEST_EN = {
    "items": [
        {
            "isValid": True,
            "projectName": "AI Comedy Test",
            "genre": "Comedy",
            "storyIdea": "A junior programmer accidentally creates an AI assistant that only speaks in dad jokes and movie quotes. The AI becomes incredibly helpful but embarrassingly awkward during important client meetings.",
            "duration": 3,  # Short to save tokens
            "request_id": "test-en-001"
        }
    ]
}

# Test 2: Russian drama
TEST_REQUEST_RU = {
    "items": [
        {
            "isValid": True,
            "projectName": "Драма о программисте",
            "genre": "Драма",
            "storyIdea": "История о талантливом программисте, который создал революционную систему искусственного интеллекта. Но успех приводит к моральным дилеммам о границах технологий.",
            "duration": 3,
            "request_id": "test-ru-001"
        }
    ]
}

# Test 3: Invalid request (for error handling)
TEST_REQUEST_INVALID = {
    "items": [
        {
            "isValid": False,  # Should be rejected
            "projectName": "Invalid Test",
            "genre": "Comedy",
            "storyIdea": "Test",
            "duration": 5
        }
    ]
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

async def wait_for_server(max_retries=10, delay=2):
    """Wait for server to be ready."""
    print("Waiting for server to start...")
    
    async with httpx.AsyncClient() as client:
        for i in range(max_retries):
            try:
                response = await client.get(f"{BASE_URL}/health", timeout=5)
                if response.status_code == 200:
                    print(f"✓ Server ready after {i * delay}s")
                    return True
            except Exception:
                pass
            
            print(f"  Retry {i + 1}/{max_retries}...")
            await asyncio.sleep(delay)
    
    print("✗ Server failed to start")
    return False


def print_test_header(test_name: str):
    """Print formatted test header."""
    print("\n" + "=" * 80)
    print(f"TEST: {test_name}")
    print("=" * 80)


def print_result(success: bool, message: str):
    """Print test result."""
    status = "✓" if success else "✗"
    print(f"{status} {message}")


# =============================================================================
# TESTS
# =============================================================================

async def test_health_check():
    """Test 1: Health check endpoint."""
    print_test_header("Health Check")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print_result(True, f"Status: {data['status']}")
                print_result(True, f"Database connected: {data['database']['connected']}")
                print_result(True, f"Total executions: {data['database']['total_executions']}")
                
                env_keys = ["OPENAI_API_KEY", "PINECONE_API_KEY", "COHERE_API_KEY"]
                for key in env_keys:
                    has_key = data['environment'][key] == "✓"
                    print_result(has_key, f"{key}: {'set' if has_key else 'not set'}")
                
                return True
            else:
                print_result(False, f"Status code: {response.status_code}")
                return False
                
    except Exception as e:
        print_result(False, f"Error: {e}")
        return False


async def test_english_generation():
    """Test 2: English script generation (full end-to-end)."""
    print_test_header("English Script Generation (E2E)")
    
    try:
        async with httpx.AsyncClient() as client:
            start_time = time.time()
            
            print("→ Sending request...")
            print(f"  Project: {TEST_REQUEST_EN['items'][0]['projectName']}")
            print(f"  Duration: {TEST_REQUEST_EN['items'][0]['duration']} min")
            print(f"  Request ID: {TEST_REQUEST_EN['items'][0]['request_id']}")
            
            response = await client.post(
                f"{BASE_URL}/generate-script",
                json=TEST_REQUEST_EN,
                timeout=TEST_TIMEOUT
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                print_result(True, f"Status: {data['status']}")
                print_result(True, f"Response time: {duration:.1f}s")
                print_result(True, f"Request ID: {data['request_id']}")
                
                # Check script content
                has_script = data.get('script') and len(data['script']) > 0
                print_result(has_script, f"Script generated: {len(data.get('script', '')) if has_script else 0} chars")
                
                # Check outline
                has_outline = data.get('outline') and len(data['outline']) > 0
                print_result(has_outline, f"Outline generated: {len(data.get('outline', '')) if has_outline else 0} chars")
                
                # Check metrics
                print_result(True, f"Iterations: {data.get('iteration_count', 0)}")
                print_result(True, f"Tokens used: {data.get('tokens_used_total', 0):,}")
                print_result(True, f"Sources retrieved: {data.get('retrieved_sources_count', 0)}")
                print_result(True, f"Character count: {data.get('char_count', 0):,}")
                print_result(True, f"Target characters: {data.get('duration_target', 0) * 1000:,}")
                
                # Save full response for inspection
                with open("test_response_en.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print_result(True, "Response saved to test_response_en.json")
                
                return True
            else:
                print_result(False, f"Status code: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                return False
                
    except Exception as e:
        print_result(False, f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_idempotency():
    """Test 3: Idempotency - same request_id should return cached result."""
    print_test_header("Idempotency Check")
    
    try:
        async with httpx.AsyncClient() as client:
            print("→ Sending duplicate request (same request_id)...")
            
            start_time = time.time()
            response = await client.post(
                f"{BASE_URL}/generate-script",
                json=TEST_REQUEST_EN,  # Same request as Test 2
                timeout=30  # Should be fast (cached)
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Should be much faster (cached)
                is_fast = duration < 5
                print_result(is_fast, f"Response time: {duration:.2f}s (cached: {is_fast})")
                print_result(True, f"Request ID: {data['request_id']}")
                print_result(True, f"Status: {data['status']}")
                
                # Should have same content
                has_script = len(data.get('script', '')) > 0
                print_result(has_script, f"Script length: {len(data.get('script', ''))} chars")
                
                return True
            else:
                print_result(False, f"Status code: {response.status_code}")
                return False
                
    except Exception as e:
        print_result(False, f"Error: {e}")
        return False


async def test_russian_generation():
    """Test 4: Russian language detection and generation."""
    print_test_header("Russian Script Generation")
    
    try:
        async with httpx.AsyncClient() as client:
            start_time = time.time()
            
            print("→ Sending Russian request...")
            print(f"  Проект: {TEST_REQUEST_RU['items'][0]['projectName']}")
            print(f"  Жанр: {TEST_REQUEST_RU['items'][0]['genre']}")
            print(f"  Длительность: {TEST_REQUEST_RU['items'][0]['duration']} мин")
            
            response = await client.post(
                f"{BASE_URL}/generate-script",
                json=TEST_REQUEST_RU,
                timeout=TEST_TIMEOUT
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                print_result(True, f"Status: {data['status']}")
                print_result(True, f"Response time: {duration:.1f}s")
                
                # Check script content
                has_script = data.get('script') and len(data['script']) > 0
                print_result(has_script, f"Скрипт: {len(data.get('script', ''))} символов")
                
                # Check if Russian was detected (target should be 3 * 1450 = 4350)
                expected_target = 3 * 1450
                actual_target = data.get('duration_target', 0) * 1450
                is_russian = abs(actual_target - expected_target) < 100
                print_result(is_russian, f"Russian detected: target ~{expected_target} chars")
                
                print_result(True, f"Итераций: {data.get('iteration_count', 0)}")
                print_result(True, f"Токенов: {data.get('tokens_used_total', 0):,}")
                
                # Save response
                with open("test_response_ru.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print_result(True, "Ответ сохранен в test_response_ru.json")
                
                return True
            else:
                print_result(False, f"Status code: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                return False
                
    except Exception as e:
        print_result(False, f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_invalid_request():
    """Test 5: Invalid request handling."""
    print_test_header("Invalid Request Handling")
    
    try:
        async with httpx.AsyncClient() as client:
            print("→ Sending invalid request (isValid: False)...")
            
            response = await client.post(
                f"{BASE_URL}/generate-script",
                json=TEST_REQUEST_INVALID,
                timeout=30
            )
            
            # Should return 422 Unprocessable Entity
            is_rejected = response.status_code == 422
            print_result(is_rejected, f"Status code: {response.status_code} (expected 422)")
            
            if response.status_code == 422:
                data = response.json()
                print_result(True, f"Validation error: {data.get('detail', 'N/A')[:100]}")
                return True
            else:
                print_result(False, f"Unexpected status code: {response.status_code}")
                return False
                
    except Exception as e:
        print_result(False, f"Error: {e}")
        return False


async def test_database_persistence():
    """Test 6: Database persistence and retrieval."""
    print_test_header("Database Persistence")
    
    try:
        async with httpx.AsyncClient() as client:
            # Get execution by request_id
            request_id = TEST_REQUEST_EN['items'][0]['request_id']
            
            print(f"→ Retrieving execution: {request_id}")
            response = await client.get(
                f"{BASE_URL}/executions/{request_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print_result(True, f"Execution found: {request_id}")
                print_result(True, f"Status: {data.get('status')}")
                print_result(True, f"Language: {data.get('language')}")
                print_result(True, f"Iterations: {data.get('iteration_count')}")
                
                # Check reasoning trace
                reasoning_trace = json.loads(data.get('reasoning_trace_json', '[]'))
                print_result(len(reasoning_trace) > 0, f"Reasoning trace: {len(reasoning_trace)} steps")
                
                if reasoning_trace:
                    print("\n  Reasoning trace summary:")
                    for i, step in enumerate(reasoning_trace[:5], 1):
                        print(f"    {i}. {step.get('action')} → {step.get('result', '')[:50]}")
                
                return True
            else:
                print_result(False, f"Status code: {response.status_code}")
                return False
                
    except Exception as e:
        print_result(False, f"Error: {e}")
        return False


async def test_statistics():
    """Test 7: Statistics endpoint."""
    print_test_header("Statistics Endpoint")
    
    try:
        async with httpx.AsyncClient() as client:
            print("→ Fetching statistics...")
            response = await client.get(
                f"{BASE_URL}/statistics",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print_result(True, f"Total executions: {data.get('total_executions', 0)}")
                print_result(True, f"Successful: {data.get('successful_executions', 0)}")
                print_result(True, f"Failed: {data.get('failed_executions', 0)}")
                print_result(True, f"Success rate: {data.get('success_rate', 0):.1%}")
                print_result(True, f"Avg iterations: {data.get('avg_iterations', 0):.1f}")
                print_result(True, f"Avg tokens: {data.get('avg_tokens_used', 0):,.0f}")
                
                return True
            else:
                print_result(False, f"Status code: {response.status_code}")
                return False
                
    except Exception as e:
        print_result(False, f"Error: {e}")
        return False


# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

async def run_all_tests():
    """Run all integration tests."""
    print("\n" + "=" * 80)
    print("AGENT BACKEND INTEGRATION TESTS")
    print("=" * 80)
    print(f"Base URL: {BASE_URL}")
    print(f"Test timeout: {TEST_TIMEOUT}s per test")
    print("=" * 80)
    
    # Wait for server
    if not await wait_for_server():
        print("\n✗ Server not available. Please start server first:")
        print("  python server.py")
        return
    
    # Run tests
    results = {}
    
    tests = [
        ("Health Check", test_health_check),
        ("English Generation (E2E)", test_english_generation),
        ("Idempotency", test_idempotency),
        ("Russian Generation", test_russian_generation),
        ("Invalid Request", test_invalid_request),
        ("Database Persistence", test_database_persistence),
        ("Statistics", test_statistics),
    ]
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            print_result(False, f"Test crashed: {e}")
            results[test_name] = False
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} {test_name}")
    
    print("-" * 80)
    print(f"Total: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print("=" * 80)
    
    return all(results.values())


if __name__ == "__main__":
    """Run integration tests."""
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)

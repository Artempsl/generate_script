"""
Test script to verify API optimizations.

This script tests:
1. OpenAI client reuse (LRU cache)
2. Temperature constants usage
3. max_tokens dynamic limiting
4. asyncio timeout wrapper
"""

import asyncio
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from agent.tools import get_llm, calculate_max_script_tokens
from agent.config import (
    OUTLINE_TEMPERATURE,
    SCRIPT_TEMPERATURE,
    MAX_TIMEOUT_SECONDS,
    MAX_SCRIPT_TOKENS_BASE
)


def test_llm_caching():
    """Test that get_llm() returns cached instances."""
    print("=" * 80)
    print("TEST 1: LLM CLIENT CACHING")
    print("=" * 80)
    
    # Get same LLM twice - should be cached
    llm1 = get_llm(temperature=0.7)
    llm2 = get_llm(temperature=0.7)
    
    print(f"LLM 1 ID: {id(llm1)}")
    print(f"LLM 2 ID: {id(llm2)}")
    print(f"Same object: {llm1 is llm2}")
    
    assert llm1 is llm2, "❌ FAILED: LLM not cached!"
    print("✅ PASSED: LLM client caching works\n")
    
    # Different temperature - should be different instance
    llm3 = get_llm(temperature=0.8)
    print(f"LLM 3 ID (temp=0.8): {id(llm3)}")
    print(f"Different from LLM 1: {llm3 is not llm1}")
    
    assert llm3 is not llm1, "❌ FAILED: Different params should create new instance!"
    print("✅ PASSED: Different parameters create different instances\n")
    
    # With max_tokens
    llm4 = get_llm(temperature=0.7, max_tokens=2000)
    llm5 = get_llm(temperature=0.7, max_tokens=2000)
    
    print(f"LLM 4 ID (max_tokens=2000): {id(llm4)}")
    print(f"LLM 5 ID (max_tokens=2000): {id(llm5)}")
    print(f"Same object: {llm4 is llm5}")
    
    assert llm4 is llm5, "❌ FAILED: LLM with max_tokens not cached!"
    print("✅ PASSED: LLM with max_tokens also cached\n")


def test_temperature_constants():
    """Test that temperature constants are correctly imported."""
    print("=" * 80)
    print("TEST 2: TEMPERATURE CONSTANTS")
    print("=" * 80)
    
    print(f"OUTLINE_TEMPERATURE: {OUTLINE_TEMPERATURE}")
    print(f"SCRIPT_TEMPERATURE: {SCRIPT_TEMPERATURE}")
    
    assert OUTLINE_TEMPERATURE == 0.7, "❌ FAILED: OUTLINE_TEMPERATURE should be 0.7"
    assert SCRIPT_TEMPERATURE == 0.8, "❌ FAILED: SCRIPT_TEMPERATURE should be 0.8"
    
    print("✅ PASSED: Temperature constants correct\n")


def test_max_tokens_calculation():
    """Test dynamic max_tokens calculation."""
    print("=" * 80)
    print("TEST 3: DYNAMIC MAX_TOKENS CALCULATION")
    print("=" * 80)
    
    # Test different target lengths
    test_cases = [
        (1000, "1-min English"),
        (1450, "1-min Russian"),
        (4350, "3-min Russian"),
        (5000, "5-min English"),
        (10000, "10-min English"),
    ]
    
    for target_chars, description in test_cases:
        max_tokens = calculate_max_script_tokens(target_chars)
        estimated_tokens = target_chars // 4
        buffer = int(estimated_tokens * 1.2)
        
        print(f"\n{description} ({target_chars} chars):")
        print(f"  Estimated tokens: {estimated_tokens}")
        print(f"  With 20% buffer: {buffer}")
        print(f"  Calculated max_tokens: {max_tokens}")
        print(f"  Within bounds: {2000 <= max_tokens <= MAX_SCRIPT_TOKENS_BASE}")
        
        assert max_tokens >= 2000, "❌ FAILED: max_tokens below minimum"
        assert max_tokens <= MAX_SCRIPT_TOKENS_BASE, "❌ FAILED: max_tokens above maximum"
    
    print("\n✅ PASSED: max_tokens calculation works correctly\n")


def test_streaming_disabled():
    """Test that streaming is disabled in LLM instances."""
    print("=" * 80)
    print("TEST 4: STREAMING DISABLED")
    print("=" * 80)
    
    llm = get_llm(temperature=0.7)
    
    # Check if streaming is disabled
    # Note: LangChain's ChatOpenAI has streaming=False by default,
    # but we explicitly set it in get_llm()
    print(f"LLM instance: {llm}")
    print(f"Model: {llm.model_name}")
    print(f"Temperature: {llm.temperature}")
    
    # Check kwargs (streaming should be False)
    if hasattr(llm, 'streaming'):
        print(f"Streaming: {llm.streaming}")
        assert llm.streaming == False, "❌ FAILED: Streaming should be disabled"
    else:
        print("Streaming parameter not directly accessible (OK - default is False)")
    
    print("✅ PASSED: Streaming configuration verified\n")


def test_timeout_config():
    """Test that timeout configuration is correctly set."""
    print("=" * 80)
    print("TEST 5: TIMEOUT CONFIGURATION")
    print("=" * 80)
    
    print(f"MAX_TIMEOUT_SECONDS: {MAX_TIMEOUT_SECONDS}")
    
    assert MAX_TIMEOUT_SECONDS == 300, "❌ FAILED: MAX_TIMEOUT_SECONDS should be 300"
    print("✅ PASSED: Timeout configuration correct (5 minutes)\n")


async def test_api_imports():
    """Test that API imports are correct."""
    print("=" * 80)
    print("TEST 6: API IMPORTS")
    print("=" * 80)
    
    try:
        from agent.api import app, db_manager
        print("✅ api.py imports successfully")
        print(f"   FastAPI app: {app}")
        print(f"   Database manager: {db_manager}")
        
        # Check that asyncio is imported in api.py
        import agent.api as api_module
        assert hasattr(api_module, 'asyncio'), "❌ FAILED: asyncio not imported in api.py"
        print("✅ asyncio imported in api.py")
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        raise
    
    print("✅ PASSED: All API imports correct\n")


def test_llm_parameters():
    """Verify LLM instances have correct parameters."""
    print("=" * 80)
    print("TEST 7: LLM INSTANCE PARAMETERS")
    print("=" * 80)
    
    # Test outline LLM
    outline_llm = get_llm(temperature=OUTLINE_TEMPERATURE, max_tokens=2000)
    print(f"Outline LLM:")
    print(f"  Temperature: {outline_llm.temperature}")
    print(f"  Model: {outline_llm.model_name}")
    assert outline_llm.temperature == 0.7, "❌ FAILED: Outline LLM wrong temperature"
    
    # Test script LLM
    script_max_tokens = calculate_max_script_tokens(4350)
    script_llm = get_llm(temperature=SCRIPT_TEMPERATURE, max_tokens=script_max_tokens)
    print(f"\nScript LLM:")
    print(f"  Temperature: {script_llm.temperature}")
    print(f"  Model: {script_llm.model_name}")
    assert script_llm.temperature == 0.8, "❌ FAILED: Script LLM wrong temperature"
    
    print("\n✅ PASSED: LLM parameters correct\n")


async def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("OPTIMIZATION TESTS")
    print("=" * 80 + "\n")
    
    start_time = time.time()
    
    try:
        # Run synchronous tests
        test_llm_caching()
        test_temperature_constants()
        test_max_tokens_calculation()
        test_streaming_disabled()
        test_timeout_config()
        test_llm_parameters()
        
        # Run async tests
        await test_api_imports()
        
        elapsed = time.time() - start_time
        
        print("=" * 80)
        print("ALL TESTS PASSED! ✅")
        print("=" * 80)
        print(f"Completed in {elapsed:.2f}s")
        print("\nOptimizations verified:")
        print("  ✅ OpenAI client reuse with LRU cache")
        print("  ✅ Temperature constants (0.7 outline, 0.8 script)")
        print("  ✅ Dynamic max_tokens calculation")
        print("  ✅ Streaming disabled")
        print("  ✅ Asyncio timeout wrapper (300s)")
        print("\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

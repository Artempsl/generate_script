"""
Quick verification test for API optimizations.

Tests only imports and function definitions without creating actual LLM instances.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """Verify all required imports and constants."""
    print("=" * 80)
    print("VERIFICATION TEST: IMPORTS AND FUNCTIONS")
    print("=" * 80 + "\n")
    
    # Test 1: Config imports
    print("1. Checking config imports...")
    from agent.config import (
        OUTLINE_TEMPERATURE,
        SCRIPT_TEMPERATURE,
        MAX_TIMEOUT_SECONDS,
        MAX_SCRIPT_TOKENS_BASE
    )
    print(f"   ✅ OUTLINE_TEMPERATURE = {OUTLINE_TEMPERATURE}")
    print(f"   ✅ SCRIPT_TEMPERATURE = {SCRIPT_TEMPERATURE}")
    print(f"   ✅ MAX_TIMEOUT_SECONDS = {MAX_TIMEOUT_SECONDS}")
    print(f"   ✅ MAX_SCRIPT_TOKENS_BASE = {MAX_SCRIPT_TOKENS_BASE}\n")
    
    # Test 2: Tools functions
    print("2. Checking tools.py functions...")
    from agent.tools import get_llm, calculate_max_script_tokens
    print(f"   ✅ get_llm function exists: {callable(get_llm)}")
    print(f"   ✅ calculate_max_script_tokens function exists: {callable(calculate_max_script_tokens)}\n")
    
    # Test 3: Calculate max_tokens examples
    print("3. Testing calculate_max_script_tokens()...")
    test_cases = [
        (1000, "1-min English"),
        (4350, "3-min Russian"),
        (10000, "10-min script"),
    ]
    
    for chars, desc in test_cases:
        tokens = calculate_max_script_tokens(chars)
        print(f"   {desc} ({chars} chars) → max_tokens={tokens}")
    print()
    
    # Test 4: API imports
    print("4. Checking api.py imports...")
    import agent.api as api_module
    
    # Check asyncio import
    import importlib
    import inspect
    api_source = inspect.getsource(api_module)
    
    has_asyncio = "import asyncio" in api_source
    has_timeout = "asyncio.wait_for" in api_source
    has_max_timeout = "MAX_TIMEOUT_SECONDS" in api_source
    
    print(f"   ✅ asyncio imported: {has_asyncio}")
    print(f"   ✅ asyncio.wait_for used: {has_timeout}")
    print(f"   ✅ MAX_TIMEOUT_SECONDS imported: {has_max_timeout}\n")
    
    # Test 5: Check tools.py for get_llm usage
    print("5. Checking tools.py for get_llm() usage...")
    import agent.tools as tools_module
    tools_source = inspect.getsource(tools_module)
    
    # Count get_llm calls
    get_llm_calls = tools_source.count("get_llm(")
    old_chatopen_ai = tools_source.count("ChatOpenAI(")
    
    print(f"   get_llm() calls found: {get_llm_calls}")
    print(f"   Old ChatOpenAI() direct calls: {old_chatopen_ai}")
    
    if get_llm_calls >= 4:
        print(f"   ✅ All tools use get_llm()")
    else:
        print(f"   ⚠ Expected 4+ get_llm() calls, found {get_llm_calls}")
    print()
    
    # Test 6: Check for temperature constants usage
    print("6. Checking temperature constants usage...")
    
    has_outline_temp = "OUTLINE_TEMPERATURE" in tools_source
    has_script_temp = "SCRIPT_TEMPERATURE" in tools_source
    
    print(f"   ✅ OUTLINE_TEMPERATURE used: {has_outline_temp}")
    print(f"   ✅ SCRIPT_TEMPERATURE used: {has_script_temp}\n")
    
    # Test 7: Check for max_tokens in script generation
    print("7. Checking max_tokens usage in script generation...")
    
    has_calc_max_tokens = "calculate_max_script_tokens" in tools_source
    
    print(f"   ✅ calculate_max_script_tokens() used: {has_calc_max_tokens}\n")
    
    # Test 8: Check for streaming=False
    print("8. Checking streaming configuration...")
    
    has_streaming_false = '"streaming": False' in tools_source or "'streaming': False" in tools_source
    
    print(f"   ✅ streaming=False set: {has_streaming_false}\n")
    
    # Summary
    print("=" * 80)
    print("VERIFICATION COMPLETE")
    print("=" * 80)
    
    all_checks = [
        ("Temperature constants defined", OUTLINE_TEMPERATURE == 0.7 and SCRIPT_TEMPERATURE == 0.8),
        ("Helper functions exist", callable(get_llm) and callable(calculate_max_script_tokens)),
        ("Asyncio timeout in API", has_asyncio and has_timeout and has_max_timeout),
        ("get_llm() usage", get_llm_calls >= 4),
        ("Temperature constants usage", has_outline_temp and has_script_temp),
        ("Dynamic max_tokens", has_calc_max_tokens),
        ("Streaming disabled", has_streaming_false),
    ]
    
    passed = sum(1 for _, check in all_checks if check)
    total = len(all_checks)
    
    print(f"\nChecks passed: {passed}/{total}\n")
    
    for check_name, result in all_checks:
        status = "✅" if result else "❌"
        print(f"{status} {check_name}")
    
    if passed == total:
        print("\n🎉 ALL OPTIMIZATIONS VERIFIED!")
        return True
    else:
        print("\n⚠ Some checks failed")
        return False


if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)

"""
Simple file-based verification of API optimizations.

Checks source code directly without importing modules.
"""

import sys
from pathlib import Path


def check_file_content(filepath, checks):
    """Check if file contains specific patterns."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    results = {}
    for name, pattern in checks.items():
        results[name] = pattern in content
    
    return results, content


def main():
    print("=" * 80)
    print("API OPTIMIZATIONS VERIFICATION")
    print("=" * 80 + "\n")
    
    agent_dir = Path(__file__).parent / "agent"
    
    # Test 1: tools.py optimizations
    print("1. Checking tools.py...")
    tools_file = agent_dir / "tools.py"
    
    tools_checks = {
        "get_llm function defined": "def get_llm(",
        "@lru_cache decorator": "@lru_cache(",
        "calculate_max_script_tokens function": "def calculate_max_script_tokens(",
        "streaming=False": '"streaming": False',
        "OUTLINE_TEMPERATURE usage": "temperature=OUTLINE_TEMPERATURE",
        "SCRIPT_TEMPERATURE usage": "temperature=SCRIPT_TEMPERATURE",
        "max_tokens calculation": "calculate_max_script_tokens(target_chars)",
    }
    
    tools_results, tools_content = check_file_content(tools_file, tools_checks)
    
    for check, passed in tools_results.items():
        status = "✅" if passed else "❌"
        print(f"   {status} {check}")
    
    # Count get_llm usages
    get_llm_count = tools_content.count("get_llm(")
    print(f"   📊 get_llm() calls: {get_llm_count}")
    
    # Count old ChatOpenAI direct instantiations (should be minimal)
    chatopen_count = tools_content.count("ChatOpenAI(")
    print(f"   📊 Direct ChatOpenAI() calls: {chatopen_count} (should be only in get_llm)")
    print()
    
    # Test 2: api.py optimizations
    print("2. Checking api.py...")
    api_file = agent_dir / "api.py"
    
    api_checks = {
        "asyncio imported": "import asyncio",
        "MAX_TIMEOUT_SECONDS imported": "MAX_TIMEOUT_SECONDS",
        "asyncio.wait_for used": "asyncio.wait_for(",
        "timeout parameter": "timeout=MAX_TIMEOUT_SECONDS",
        "TimeoutError handling": "asyncio.TimeoutError",
    }
    
    api_results, api_content = check_file_content(api_file, api_checks)
    
    for check, passed in api_results.items():
        status = "✅" if passed else "❌"
        print(f"   {status} {check}")
    print()
    
    # Test 3: config.py constants
    print("3. Checking config.py...")
    config_file = agent_dir / "config.py"
    
    config_checks = {
        "OUTLINE_TEMPERATURE = 0.7": "OUTLINE_TEMPERATURE = 0.7",
        "SCRIPT_TEMPERATURE = 0.8": "SCRIPT_TEMPERATURE = 0.8",
        "MAX_TIMEOUT_SECONDS = 300": "MAX_TIMEOUT_SECONDS = 300",
        "MAX_SCRIPT_TOKENS_BASE": "MAX_SCRIPT_TOKENS_BASE",
    }
    
    config_results, _ = check_file_content(config_file, config_checks)
    
    for check, passed in config_results.items():
        status = "✅" if passed else "❌"
        print(f"   {status} {check}")
    print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80 + "\n")
    
    all_results = [
        ("tools.py", tools_results),
        ("api.py", api_results),
        ("config.py", config_results),
    ]
    
    total_checks = 0
    passed_checks = 0
    
    for filename, results in all_results:
        file_passed = sum(results.values())
        file_total = len(results)
        total_checks += file_total
        passed_checks += file_passed
        
        print(f"{filename}: {file_passed}/{file_total} checks passed")
    
    print(f"\nTotal: {passed_checks}/{total_checks} checks passed")
    
    if passed_checks == total_checks:
        print("\n🎉 ALL OPTIMIZATIONS SUCCESSFULLY IMPLEMENTED!")
        print("\nImplemented optimizations:")
        print("  ✅ Global LLM factory with @lru_cache (client reuse)")
        print("  ✅ Temperature constants (OUTLINE=0.7, SCRIPT=0.8)")
        print("  ✅ Dynamic max_tokens calculation")
        print("  ✅ Streaming disabled (streaming=False)")
        print("  ✅ Asyncio timeout wrapper (300s)")
        return True
    else:
        print(f"\n⚠ {total_checks - passed_checks} checks failed")
        return False


if __name__ == "__main__":
    success = main()
    print()
    sys.exit(0 if success else 1)

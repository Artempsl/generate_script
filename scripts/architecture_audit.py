"""
Comprehensive architecture audit for the agent system.
Checks:
1. Idempotency (request_id check)
2. Retry logic with exponential backoff
3. Error handling with HTTP 500
4. Structured logging
"""
import re
from pathlib import Path


def check_idempotency():
    """Check if request_id idempotency is implemented."""
    print("\n" + "=" * 80)
    print("1. IDEMPOTENCY CHECK")
    print("=" * 80)
    
    api_file = Path("agent/api.py")
    content = api_file.read_text(encoding='utf-8')
    
    checks = {
        "Check for existing execution": "existing.*get_execution|get_execution.*request_id",
        "Return cached result": "existing.*return|return.*existing",
        "Prevent duplicate generation": "if existing"
    }
    
    for check_name, pattern in checks.items():
        if re.search(pattern, content, re.IGNORECASE):
            print(f"  ✓ {check_name}")
        else:
            print(f"  ✗ {check_name}")


def check_retry_logic():
    """Check retry logic with exponential backoff."""
    print("\n" + "=" * 80)
    print("2. RETRY LOGIC CHECK")
    print("=" * 80)
    
    tools_file = Path("agent/tools.py")
    content = tools_file.read_text(encoding='utf-8')
    
    # Check tenacity import
    if "from tenacity import retry" in content:
        print("  ✓ Tenacity library imported")
    else:
        print("  ✗ Tenacity library NOT imported")
        return
    
    # Find all @retry decorators
    retry_pattern = r'@retry\([^)]+\)'
    retry_decorators = re.findall(retry_pattern, content, re.DOTALL)
    
    print(f"\n  Found {len(retry_decorators)} @retry decorators:")
    
    for decorator in retry_decorators[:5]:  # Show first 5
        # Extract stop and wait config
        if "stop_after_attempt" in decorator:
            attempts = re.search(r'stop_after_attempt\((\d+)\)', decorator)
            if attempts:
                print(f"    • Attempts: {attempts.group(1)}")
        
        if "wait_exponential" in decorator:
            print(f"    • Exponential backoff: ✓")
    
    # Check which tools have retry
    tools_with_retry = [
        ("retrieve_tool", "Pinecone retrieval"),
        ("web_search_tool", "Web search"),
        ("reasoning_tool", "ReAct reasoning"),
        ("generate_outline_tool", "Outline generation"),
        ("generate_script_tool", "Script generation"),
        ("segment_script_tool", "Segmentation"),
        ("generate_tts_tool", "TTS audio generation")
    ]
    
    print("\n  Tools with @retry decorator:")
    for tool_name, description in tools_with_retry:
        # Check if tool has @retry before its definition
        pattern = rf'@retry.*?def {tool_name}\('
        if re.search(pattern, content, re.DOTALL):
            print(f"    ✓ {description} ({tool_name})")
        else:
            print(f"    ✗ {description} ({tool_name}) - NO RETRY")


def check_error_handling():
    """Check error handling with HTTP 500."""
    print("\n" + "=" * 80)
    print("3. ERROR HANDLING CHECK")
    print("=" * 80)
    
    api_file = Path("agent/api.py")
    content = api_file.read_text(encoding='utf-8')
    
    checks = {
        "HTTPException with 500": r'HTTPException.*status_code=500',
        "Timeout handling": r'TimeoutError|asyncio\.TimeoutError',
        "Save failed execution to DB": r'status="error".*save_execution',
        "Error logging": r'logger\.(error|exception)|print.*error'
    }
    
    for check_name, pattern in checks.items():
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            print(f"  ✓ {check_name} ({len(matches)} instances)")
        else:
            print(f"  ✗ {check_name}")


def check_logging():
    """Check structured logging."""
    print("\n" + "=" * 80)
    print("4. STRUCTURED LOGGING CHECK")
    print("=" * 80)
    
    files_to_check = [
        ("agent/tools.py", "Tools"),
        ("agent/graph.py", "Graph"),
        ("agent/api.py", "API")
    ]
    
    for file_path, module_name in files_to_check:
        path = Path(file_path)
        if not path.exists():
            print(f"  ✗ {module_name}: File not found")
            continue
            
        content = path.read_text(encoding='utf-8')
        
        # Check logging setup
        has_logger = "import logging" in content or "from logging import" in content
        has_logger_instance = "logger = logging.getLogger" in content
        has_info_logs = "logger.info" in content
        has_error_logs = "logger.error" in content
        
        print(f"\n  {module_name} ({file_path}):")
        print(f"    Logger setup:    {'✓' if has_logger else '✗'}")
        print(f"    Logger instance: {'✓' if has_logger_instance else '✗'}")
        print(f"    Info logging:    {'✓' if has_info_logs else '✗'}")
        print(f"    Error logging:   {'✓' if has_error_logs else '✗'}")


def check_max_iterations():
    """Check max iterations limit."""
    print("\n" + "=" * 80)
    print("5. MAX ITERATIONS CHECK")
    print("=" * 80)
    
    files = ["agent/graph.py", "agent/models.py", "agent/api.py"]
    
    for file_path in files:
        path = Path(file_path)
        if not path.exists():
            continue
            
        content = path.read_text(encoding='utf-8')
        
        if "max_iterations" in content.lower():
            # Find the value
            match = re.search(r'max_iterations["\']?\s*[:=]\s*(\d+)', content)
            if match:
                print(f"  ✓ Found in {file_path}: max_iterations = {match.group(1)}")
                
                # Check if there's iteration limit enforcement
                if "iteration.*>.*max_iterations" in content or "iteration.*>=.*max_iterations" in content:
                    print(f"    ✓ Iteration limit enforced")


def main():
    print("\n" + "=" * 80)
    print("ARCHITECTURE AUDIT REPORT")
    print("=" * 80)
    
    check_idempotency()
    check_retry_logic()
    check_error_handling()
    check_logging()
    check_max_iterations()
    
    print("\n" + "=" * 80)
    print("AUDIT COMPLETE")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()

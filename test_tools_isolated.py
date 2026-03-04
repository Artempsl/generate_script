"""
Test individual tools in isolation to identify the blocking component.
"""
import sys
import time
import traceback
from pathlib import Path

# Add agent package to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("ISOLATED TOOLS TEST")
print("=" * 60)

# Test 1: Import tools
print("\n[1/5] Testing imports...")
try:
    from agent.tools import (
        retrieve_tool,
        web_search_tool,
        synthesize_tool,
        generate_outline_tool,
        generate_script_tool,
        validate_tool
    )
    print("✓ All tools imported successfully")
except Exception as e:
    print(f"✗ Import failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 2: Pinecone retrieval
print("\n[2/5] Testing Pinecone retrieval...")
start = time.time()
try:
    result = retrieve_tool(
        query="storytelling comedy best practices",
        language="en",
        top_k=3
    )
    elapsed = time.time() - start
    print(f"✓ Pinecone retrieval completed in {elapsed:.2f}s")
    print(f"  Success: {result['success']}")
    print(f"  Documents: {len(result.get('documents', []))}")
    if not result['success']:
        print(f"  Error: {result.get('error', 'Unknown')}")
except Exception as e:
    elapsed = time.time() - start
    print(f"✗ Pinecone retrieval failed after {elapsed:.2f}s: {e}")
    traceback.print_exc()

# Test 3: Web search (SerpAPI - optional)
print("\n[3/5] Testing web search (SerpAPI)...")
start = time.time()
try:
    result = web_search_tool(
        query="comedy script writing tips",
        language="en"
    )
    elapsed = time.time() - start
    print(f"✓ Web search completed in {elapsed:.2f}s")
    print(f"  Success: {result['success']}")
    print(f"  Results: {len(result.get('results', []))}")
    if not result['success']:
        print(f"  Error: {result.get('error', 'Unknown')}")
except Exception as e:
    elapsed = time.time() - start
    print(f"✗ Web search failed after {elapsed:.2f}s: {e}")
    traceback.print_exc()

# Test 4: Synthesize (OpenAI)
print("\n[4/5] Testing synthesize (OpenAI)...")
start = time.time()
try:
    result = synthesize_tool(
        documents=["Comedy needs good timing.", "Use relatable situations."],
        search_results=["Keep it simple."],
        project_name="Test",
        genre="Comedy",
        idea="A robot learns comedy",
        language="en"
    )
    elapsed = time.time() - start
    print(f"✓ Synthesize completed in {elapsed:.2f}s")
    print(f"  Success: {result['success']}")
    print(f"  Synthesis length: {len(result.get('synthesis', ''))}")
    if not result['success']:
        print(f"  Error: {result.get('error', 'Unknown')}")
except Exception as e:
    elapsed = time.time() - start
    print(f"✗ Synthesize failed after {elapsed:.2f}s: {e}")
    traceback.print_exc()

# Test 5: Generate outline (OpenAI)
print("\n[5/5] Testing generate_outline (OpenAI)...")
start = time.time()
try:
    result = generate_outline_tool(
        synthesis="Use comedy timing and relatable situations.",
        genre="Comedy",
        idea="A robot learns comedy",
        duration=1,
        language="en"
    )
    elapsed = time.time() - start
    print(f"✓ Generate outline completed in {elapsed:.2f}s")
    print(f"  Success: {result['success']}")
    print(f"  Outline length: {len(result.get('outline', ''))}")
    if not result['success']:
        print(f"  Error: {result.get('error', 'Unknown')}")
except Exception as e:
    elapsed = time.time() - start
    print(f"✗ Generate outline failed after {elapsed:.2f}s: {e}")
    traceback.print_exc()

print("\n" + "=" * 60)
print("ISOLATED TOOLS TEST COMPLETE")
print("=" * 60)

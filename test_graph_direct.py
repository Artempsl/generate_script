"""
Test agent graph with minimal state to identify blocking node.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from agent.models import create_initial_state, ScriptRequestItem
from agent.graph import create_agent_graph
import time

print("=" * 60)
print("AGENT GRAPH EXECUTION TEST")
print("="  * 60)

#Create minimal request
request = ScriptRequestItem(
    isValid=True,
    projectName="Graph Test",
    genre="Comedy",
    storyIdea="A simple test story",
    duration=1,
    request_id=f"graph-test-{int(time.time())}"
)

print("\n1. Creating initial state...")
initial_state = create_initial_state(request)
print(f"   Language: {initial_state['language']}")
print(f"   Target chars: {initial_state['target_chars']}")
print(f"   State keys: {list(initial_state.keys())}")
print(f"   State type: {type(initial_state)}")

print("\n2. Creating graph...")
graph = create_agent_graph()
print("   ✓ Graph compiled")

print("\n3. Executing graph...")
print("   (This may take 30-90 seconds)")
start = time.time()

try:
    final_state = graph.invoke(initial_state)
    elapsed = time.time() - start
    
    print(f"\n✅ Graph execution complete in {elapsed:.1f}s")
    print(f"\n4. Results:")
    print(f"   Status: {final_state.get('error', 'Success')}")
    print(f"   Iterations: {final_state.get('iteration', 0)}")
    print(f"   Script length: {len(final_state.get('script', ''))} chars")
    print(f"   Tokens used: {final_state.get('tokens_used', 0)}")
    print(f"   Reasoning steps: {len(final_state.get('reasoning_trace', []))}")
    
except Exception as e:
    elapsed = time.time() - start
    print(f"\n❌ Graph execution failed after {elapsed:.1f}s")
    print(f"   Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)

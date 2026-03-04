"""
Minimal LangGraph test to check if graph execution works.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from typing import TypedDict
from langgraph.graph import StateGraph, END

class SimpleState(TypedDict):
    counter: int
    message: str

def node1(state: SimpleState) -> SimpleState:
    print("  Node 1: Incrementing counter")
    state['counter'] = state.get('counter', 0) + 1
    state['message'] = f"Node 1 executed (counter={state['counter']})"
    return state

def node2(state: SimpleState) -> SimpleState:
    print("  Node 2: Incrementing counter")
    state['counter'] = state.get('counter', 0) + 1
    state['message'] = f"Node 2 executed (counter={state['counter']})"
    return state

print("=" * 60)
print("MINIMAL LANGGRAPH TEST")
print("=" * 60)

print("\n1. Creating graph...")
workflow = StateGraph(SimpleState)
workflow.add_node("node1", node1)
workflow.add_node("node2", node2)
workflow.set_entry_point("node1")
workflow.add_edge("node1", "node2")
workflow.add_edge("node2", END)

print("2. Compiling graph...")
graph = workflow.compile()

print("3. Executing graph...")
initial_state: SimpleState = {"counter": 0, "message": ""}
final_state = graph.invoke(initial_state)

print(f"\n4. Result:")
print(f"   Counter: {final_state['counter']}")
print(f"   Message: {final_state['message']}")

if final_state['counter'] == 2:
    print("\n✅ LangGraph works correctly!")
else:
    print(f"\n❌ Something wrong: counter={final_state['counter']}, expected 2")

print("=" * 60)

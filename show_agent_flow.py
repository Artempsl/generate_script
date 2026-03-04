"""Show full agent flow with prompts."""
import sqlite3
import json

conn = sqlite3.connect('agent.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT reasoning_trace_json
    FROM executions
    WHERE request_id LIKE 'test-horror-%'
    ORDER BY created_at DESC
    LIMIT 1
""")

row = cursor.fetchone()
trace = json.loads(row[0])

print("=" * 80)
print("HORROR SCRIPT GENERATION - FULL AGENT FLOW")
print("=" * 80)

# Group by unique steps
seen_steps = set()
unique_steps = []
for item in trace:
    step_key = (item['step'], item['action'])
    if step_key not in seen_steps:
        seen_steps.add(step_key)
        unique_steps.append(item)

print(f"\nTotal unique steps: {len(unique_steps)}")
print("\n" + "=" * 80)

for item in unique_steps[:20]:  # Show first 20 unique steps
    print(f"\nSTEP {item['step']}: {item['action']}")
    print("-" * 80)
    print(f"Result: {item['result']}")
    print(f"Tokens: {item['tokens_used']}")
    print(f"Time: {item['timestamp']}")

print("\n" + "=" * 80)
print("KEY STEPS SUMMARY:")
print("=" * 80)

# Find key steps
retrieve_steps = [s for s in unique_steps if 'retrieve' in s['action'].lower()]
synth_steps = [s for s in unique_steps if 'synth' in s['action'].lower()]
outline_steps = [s for s in unique_steps if 'outline' in s['action'].lower()]
script_steps = [s for s in unique_steps if 'script' in s['action'].lower() and 'outline' not in s['action'].lower()]

print(f"\n✅ Pinecone retrieval: {len(retrieve_steps)} step(s)")
for s in retrieve_steps[:1]:
    print(f"   → {s['result']}")

print(f"\n✅ Synthesis: {len(synth_steps)} step(s)")
for s in synth_steps[:1]:
    print(f"   → {s['result']}")

print(f"\n✅ Outline generation: {len(outline_steps)} step(s)")
for s in outline_steps[:1]:
    print(f"   → {s['result']}")

print(f"\n✅ Script generation: {len(script_steps)} step(s)")
for s in script_steps[:3]:
    print(f"   → {s['result']}")

conn.close()

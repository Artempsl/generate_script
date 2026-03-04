"""Check reasoning trace structure."""
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

print(f"Type: {type(trace)}")
print(f"Length: {len(trace)}")

if isinstance(trace, list) and len(trace) > 0:
    print(f"\nFirst item type: {type(trace[0])}")
    print(f"First item keys: {list(trace[0].keys())}")
    print(f"\nFirst 3 items:")
    for i in range(min(3, len(trace))):
        print(f"\n{i+1}. {json.dumps(trace[i], indent=2)[:500]}...")

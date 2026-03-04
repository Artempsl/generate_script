"""Show ReAct reasoning from database."""
import sqlite3
import json

conn = sqlite3.connect('agent.db')
cursor = conn.cursor()

# Get latest execution with reasoning
cursor.execute("""
    SELECT request_id, genre, project_name, reasoning_trace_json, created_at
    FROM executions
    ORDER BY created_at DESC
    LIMIT 1
""")

row = cursor.fetchone()

if row:
    request_id, genre, project_name, reasoning_json, created_at = row
    reasoning_trace = json.loads(reasoning_json)
    
    print("=" * 80)
    print(f"REACT REASONING ANALYSIS")
    print("=" * 80)
    print(f"Request: {request_id}")
    print(f"Project: {project_name}")
    print(f"Genre: {genre}")
    print(f"Generated: {created_at}")
    print("=" * 80)
    
    # Find reasoning step
    reasoning_steps = [s for s in reasoning_trace if 'react_reasoning' in s.get('action', '').lower() or 'reasoning' in s.get('action', '').lower()]
    
    if reasoning_steps:
        print(f"\n🧠 REACT REASONING STEP FOUND!")
        print("=" * 80)
        
        for step in reasoning_steps:
            print(f"\nStep {step['step']}: {step['action']}")
            print(f"Time: {step['timestamp']}")
            print(f"Tokens: {step['tokens_used']}")
            print(f"\nResult:")
            print("-" * 80)
            result_text = step.get('result', '')
            # Parse if it's a dict string
            if 'Strategy:' in result_text:
                print(result_text)
            else:
                print(result_text[:500])
            print("-" * 80)
    else:
        print("\n⚠️ No ReAct reasoning step found in trace")
        print("This might be an old execution before reasoning was added\n")
        
    # Show flow summary
    print("\n" + "=" * 80)
    print("EXECUTION FLOW SUMMARY:")
    print("=" * 80)
    
    unique_actions = []
    seen = set()
    for item in reasoning_trace:
        action = item.get('action', '')
        if action not in seen:
            seen.add(action)
            unique_actions.append(item)
    
    for i, item in enumerate(unique_actions[:15], 1):
        action = item['action']
        result = item['result']
        tokens = item.get('tokens_used', 0)
        
        # Highlight reasoning step
        if 'reasoning' in action.lower():
            print(f"\n{i}. 🧠 {action.upper()} (NEW!)")
        else:
            print(f"\n{i}. {action}")
        
        print(f"   → {result[:100]}{'...' if len(result) > 100 else ''}")
        print(f"   Tokens: {tokens}")
    
    print("\n" + "=" * 80)
    
else:
    print("No executions found in database")

conn.close()

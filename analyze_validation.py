import sqlite3
import json

conn = sqlite3.connect('agent.db')
cur = conn.cursor()

# Get the betrayal test
result = cur.execute('''
    SELECT request_id, iteration_count, char_count, target_chars, 
           reasoning_trace_json
    FROM executions
    WHERE request_id LIKE 'test-betrayal%'
    ORDER BY created_at DESC
    LIMIT 1
''').fetchone()

if result:
    req_id, iterations, actual, target, trace_json = result
    
    print("=" * 80)
    print("VALIDATION ANALYSIS")
    print("=" * 80)
    print(f"Request: {req_id}")
    print(f"Iterations: {iterations}")
    print(f"Actual: {actual} chars")
    print(f"Target: {target} chars")
    print(f"Ratio: {actual/target*100:.1f}%")
    print()
    
    trace = json.loads(trace_json)
    
    # Find validation steps
    validation_steps = [step for step in trace if 'validate' in step.get('action', '').lower()]
    generate_steps = [step for step in trace if 'generate_script' in step.get('action', '')]
    regenerate_steps = [step for step in trace if 'regenerate' in step.get('action', '')]
    
    print(f"Total steps in trace: {len(trace)}")
    print(f"Validation steps: {len(validation_steps)}")
    print(f"Generate steps: {len(generate_steps)}")
    print(f"Regenerate steps: {len(regenerate_steps)}")
    print()
    
    # Show validation results
    print("=" * 80)
    print("VALIDATION STEPS:")
    print("=" * 80)
    for i, step in enumerate(validation_steps):
        print(f"\nValidation {i+1}:")
        print(f"  Step: {step.get('step')}")
        print(f"  Time: {step.get('timestamp')}")
        print(f"  Result: {step.get('result')}")
    
    # Show generation flow
    print("\n" + "=" * 80)
    print("GENERATION FLOW:")
    print("=" * 80)
    
    script_gen_steps = [s for s in trace if 'generate_script' in s.get('action', '') or 'regenerate' in s.get('action', '')]
    for i, step in enumerate(script_gen_steps):
        print(f"\n{i+1}. {step.get('action')}:")
        print(f"   Result: {step.get('result')}")
        print(f"   Time: {step.get('timestamp')}")
    
    # Check last few steps to see why it ended
    print("\n" + "=" * 80)
    print("LAST 10 STEPS:")
    print("=" * 80)
    for step in trace[-10:]:
        print(f"{step.get('step'):3d}. {step.get('action'):<30} → {step.get('result')}")

else:
    print("Test not found")

conn.close()

import sqlite3
import json

conn = sqlite3.connect('agent.db')
cur = conn.cursor()

# Check for the betrayal test
result = cur.execute('''
    SELECT request_id, project_name, genre, duration, language,
           char_count, iteration_count, status, tokens_used_total,
           retrieved_sources_count, created_at, script,
           reasoning_trace_json
    FROM executions
    WHERE request_id LIKE 'test-betrayal%'
    ORDER BY created_at DESC
    LIMIT 1
''').fetchone()

if result:
    (req_id, proj, genre, dur, lang, chars, iters, status, tokens, 
     sources, created, script, trace_json) = result
    
    print("=" * 80)
    print("FAMILY BETRAYAL TEST FOUND")
    print("=" * 80)
    print(f"Request ID: {req_id}")
    print(f"Project: {proj}")
    print(f"Genre: {genre}")
    print(f"Duration: {dur} min")
    print(f"Language: {lang}")
    print(f"Status: {status}")
    print(f"Characters: {chars}")
    print(f"Iterations: {iters}")
    print(f"Tokens: {tokens}")
    print(f"Sources from Pinecone: {sources}")
    print(f"Created: {created}")
    
    # Save script to file
    filename = f"generated_script_{req_id.split('-')[-1]}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"PROJECT: {proj}\n")
        f.write(f"GENRE: {genre}\n")
        f.write(f"DURATION: {dur} min\n")
        f.write(f"LANGUAGE: {lang}\n")
        f.write(f"LENGTH: {chars} characters\n")
        f.write(f"ITERATIONS: {iters}\n")
        f.write(f"TOKENS USED: {tokens}\n")
        f.write(f"SOURCES: {sources} from Pinecone\n")
        f.write(f"GENERATED: {created}\n")
        f.write(f"\n{'=' * 70}\n\n")
        f.write(script)
    
    print(f"\n✓ Script saved to: {filename}")
    
    # Check for ReAct reasoning in trace
    if trace_json:
        trace = json.loads(trace_json)
        reasoning_steps = [step for step in trace if step.get('action') == 'react_reasoning']
        if reasoning_steps:
            print(f"\n🧠 ReAct reasoning found: {len(reasoning_steps)} step(s)")
            step = reasoning_steps[0]
            result_data = step.get('result', {})
            if isinstance(result_data, str):
                # Try to parse if it's string
                print(f"   Reasoning length: {len(result_data)} chars")
            else:
                strategy = result_data.get('strategy', {})
                print(f"   Strategy: {strategy}")
        else:
            print("\n⚠ No ReAct reasoning found in trace")
    
    print(f"\n" + "=" * 80)
    print("SCRIPT PREVIEW (first 800 chars):")
    print("=" * 80)
    print(script[:800])
    if len(script) > 800:
        print("\n[... continues ...]")
    
else:
    print("❌ No betrayal test found in database")
    print("\nAll recent executions:")
    results = cur.execute('''
        SELECT request_id, genre, duration, created_at 
        FROM executions 
        ORDER BY created_at DESC 
        LIMIT 5
    ''').fetchall()
    for row in results:
        print(f"  {row[3]} | {row[0]} | {row[1]} | {row[2]}min")

conn.close()

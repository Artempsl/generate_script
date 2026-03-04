"""Analyze reasoning trace to show agent steps and prompts."""
import sqlite3
import json

conn = sqlite3.connect('agent.db')
cursor = conn.cursor()

# Get horror script reasoning trace
cursor.execute("""
    SELECT request_id, reasoning_trace_json
    FROM executions
    WHERE request_id LIKE 'test-horror-%'
    ORDER BY created_at DESC
    LIMIT 1
""")

row = cursor.fetchone()

if row:
    request_id, reasoning_json = row
    reasoning_trace = json.loads(reasoning_json)
    
    print("=" * 80)
    print(f"REASONING TRACE ANALYSIS: {request_id}")
    print("=" * 80)
    print(f"\nTotal steps: {len(reasoning_trace)}")
    print("\n" + "=" * 80)
    
    for i, step in enumerate(reasoning_trace, 1):
        print(f"\nSTEP {i}: {step['tool']}")
        print("-" * 80)
        print(f"Observation: {step['observation'][:150]}...")
        
        # Show detailed info for key steps
        if step['tool'] == 'retrieve':
            print("\n🔍 PINECONE RETRIEVAL DETAILS:")
            obs = step['observation']
            if 'sources_count' in obs:
                print(f"  ✓ Sources found: {obs.get('sources_count', 0)}")
                print(f"  ✓ Tokens from Pinecone: {obs.get('tokens_used', 0)}")
                if obs.get('context'):
                    context_len = len(obs['context'])
                    print(f"  ✓ Context length: {context_len} chars")
                    print(f"\n  Context preview (first 400 chars):")
                    print(f"  {obs['context'][:400]}...")
        
        elif step['tool'] == 'synthesize':
            print("\n🧩 SYNTHESIS DETAILS:")
            obs = step['observation']
            if obs.get('synthesized_context'):
                synth_len = len(obs['synthesized_context'])
                print(f"  ✓ Synthesized context: {synth_len} chars")
                print(f"  ✓ Tokens used: {obs.get('tokens_used', 0)}")
                print(f"\n  Synthesized context preview (first 500 chars):")
                print(f"  {obs['synthesized_context'][:500]}...")
        
        elif step['tool'] == 'generate_outline':
            print("\n📝 OUTLINE GENERATION DETAILS:")
            obs = step['observation']
            if obs.get('outline'):
                outline_len = len(obs['outline'])
                print(f"  ✓ Outline length: {outline_len} chars")
                print(f"  ✓ Tokens used: {obs.get('tokens_used', 0)}")
                print(f"\n  Outline preview (first 600 chars):")
                print(f"  {obs['outline'][:600]}...")
        
        elif step['tool'] == 'generate_script':
            print("\n🎬 SCRIPT GENERATION DETAILS:")
            obs = step['observation']
            if obs.get('script'):
                script_len = len(obs['script'])
                print(f"  ✓ Script length: {script_len} chars")
                print(f"  ✓ Tokens used: {obs.get('tokens_used', 0)}")
                print(f"\n  Script preview (first 400 chars):")
                print(f"  {obs['script'][:400]}...")
        
        print("")
    
    print("\n" + "=" * 80)
    print("VERIFICATION:")
    print("=" * 80)
    
    # Check if Pinecone was used
    retrieve_steps = [s for s in reasoning_trace if s['tool'] == 'retrieve']
    if retrieve_steps:
        sources = retrieve_steps[0]['observation'].get('sources_count', 0)
        print(f"✅ Pinecone queried: {len(retrieve_steps)} time(s)")
        print(f"✅ Sources retrieved: {sources}")
    else:
        print("❌ No Pinecone retrieval found!")
    
    # Check synthesis
    synth_steps = [s for s in reasoning_trace if s['tool'] == 'synthesize']
    if synth_steps:
        print(f"✅ Context synthesized: {len(synth_steps)} time(s)")
    else:
        print("❌ No synthesis found!")
    
    print("\n" + "=" * 80)
    
else:
    print("No reasoning trace found")

conn.close()

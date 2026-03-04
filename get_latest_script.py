import sqlite3
from datetime import datetime

conn = sqlite3.connect('agent.db')
cur = conn.cursor()

# Get the latest script
result = cur.execute('''
    SELECT request_id, project_name, genre, duration, language, 
           script, char_count, iteration_count, tokens_used_total, 
           retrieved_sources_count, created_at
    FROM executions
    ORDER BY created_at DESC
    LIMIT 1
''').fetchone()

if result:
    (request_id, project_name, genre, duration, language, 
     script, char_count, iteration_count, tokens_used_total, 
     sources_count, created_at) = result
    
    filename = f"generated_script_{request_id.split('-')[-1]}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"PROJECT: {project_name}\n")
        f.write(f"GENRE: {genre}\n")
        f.write(f"DURATION: {duration} min\n")
        f.write(f"LANGUAGE: {language}\n")
        f.write(f"LENGTH: {char_count} characters\n")
        f.write(f"ITERATIONS: {iteration_count}\n")
        f.write(f"TOKENS USED: {tokens_used_total}\n")
        f.write(f"SOURCES: {sources_count} from Pinecone\n")
        f.write(f"GENERATED: {created_at}\n")
        f.write(f"\n{'=' * 70}\n\n")
        f.write(script)
    
    print(f"✓ Script saved to: {filename}")
    print(f"\nDetails:")
    print(f"  Genre: {genre}")
    print(f"  Length: {char_count} chars")
    print(f"  Iterations: {iteration_count}")
    print(f"  Tokens: {tokens_used_total}")
    print(f"  Sources: {sources_count}")
    print(f"\nScript preview (first 500 chars):")
    print("=" * 70)
    print(script[:500])
    if len(script) > 500:
        print("\n[... continues ...]")
else:
    print("No scripts found in database")

conn.close()

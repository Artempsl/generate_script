"""Extract horror script from database."""
import sqlite3

conn = sqlite3.connect('agent.db')
cursor = conn.cursor()

# Get horror script
cursor.execute("""
    SELECT request_id, project_name, genre, duration, language,
           char_count, iteration_count, tokens_used_total, 
           retrieved_sources_count, script, created_at
    FROM executions
    WHERE request_id LIKE 'test-horror-%'
    ORDER BY created_at DESC
    LIMIT 1
""")

row = cursor.fetchone()

if row:
    request_id, project_name, genre, duration, language, char_count, \
        iterations, tokens, sources, script, created_at = row
    
    # Create filename
    timestamp = request_id.split('-')[-1]
    filename = f"generated_script_{timestamp}.txt"
    
    # Write to file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"PROJECT: {project_name}\n")
        f.write(f"GENRE: {genre}\n")
        f.write(f"DURATION: {duration} min\n")
        f.write(f"LANGUAGE: {language}\n")
        f.write(f"LENGTH: {char_count} characters\n")
        f.write(f"ITERATIONS: {iterations}\n")
        f.write(f"TOKENS USED: {tokens}\n")
        f.write(f"SOURCES: {sources}\n")
        f.write(f"GENERATED: {created_at}\n")
        f.write(f"\n{'=' * 70}\n\n")
        f.write(script)
    
    print(f"✓ Horror script saved to: {filename}")
    print(f"\nMetadata:")
    print(f"  Project: {project_name}")
    print(f"  Genre: {genre}")
    print(f"  Duration: {duration} min")
    print(f"  Language: {language}")
    print(f"  Length: {char_count} characters")
    print(f"  Iterations: {iterations}")
    print(f"  Tokens: {tokens}")
    print(f"  Sources from Pinecone: {sources}")
    print(f"  Generated: {created_at}")
    print(f"\nScript preview (first 600 chars):")
    print("=" * 70)
    print(script[:600])
    print("...")
else:
    print("No horror script found in database")

conn.close()

"""Check Comedy Test in database."""
import sqlite3
import json

conn = sqlite3.connect('agent.db')
cursor = conn.cursor()

# Find Comedy Test
print("=" * 80)
print("SEARCHING FOR COMEDY TEST IN DATABASE")
print("=" * 80)

cursor.execute("""
    SELECT request_id, project_name, genre, char_count, audio_files_count, 
           script, segments_json
    FROM executions 
    WHERE project_name LIKE '%Comedy%' OR request_id LIKE '%003%'
    ORDER BY created_at DESC 
    LIMIT 3
""")

rows = cursor.fetchall()

if not rows:
    print("\n❌ No Comedy Test records found in database")
    print("\nChecking all recent records:")
    cursor.execute("""
        SELECT request_id, project_name, genre, char_count 
        FROM executions 
        ORDER BY created_at DESC 
        LIMIT 5
    """)
    recent = cursor.fetchall()
    for row in recent:
        print(f"  - {row[0]} | {row[1]} | {row[2]} | {row[3]} chars")
else:
    print(f"\n✅ Found {len(rows)} Comedy Test record(s):\n")
    
    for i, row in enumerate(rows, 1):
        request_id, project_name, genre, char_count, audio_files_count, script, segments_json = row
        
        print(f"Record #{i}:")
        print(f"  Request ID: {request_id}")
        print(f"  Project: {project_name}")
        print(f"  Genre: {genre}")
        print(f"  Char count: {char_count}")
        print(f"  Audio files: {audio_files_count}")
        print(f"\n  Script (first 200 chars):")
        print(f"  {script[:200] if script else 'N/A'}...")
        
        if segments_json:
            try:
                segments = json.loads(segments_json)
                print(f"\n  Segments ({len(segments)} total):")
                for seg in segments[:3]:
                    print(f"    [{seg.get('segment_index')}] {seg.get('text', '')[:80]}...")
                    if 'audio_url' in seg:
                        print(f"        Audio: {seg['audio_url']}")
            except json.JSONDecodeError:
                print(f"\n  Segments: JSON decode error")
        else:
            print(f"\n  Segments: None")
        
        print("\n" + "-" * 80 + "\n")

conn.close()

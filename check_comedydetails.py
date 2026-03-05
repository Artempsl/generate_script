"""Check Comedy Test results."""
import sqlite3
import json

conn = sqlite3.connect('agent.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT script, segments_json, audio_files_count, iteration_count
    FROM executions 
    WHERE request_id = 'test-segments-pipeline-003'
""")

row = cursor.fetchone()

if not row:
    print("❌ No Comedy Test found!")
else:
    script, segments_json, audio_files_count, iteration_count = row
    
    print("=" * 80)
    print("COMEDY TEST RESULTS")
    print("=" * 80)
    
    print(f"\n✅ Script ({len(script)} chars) - Iterations: {iteration_count}")
    print(f"\nScript preview (first 500 chars):")
    print(script[:500])
    print("...")
    
    if segments_json:
        segments = json.loads(segments_json)
        print(f"\n✅ Segments: {len(segments)} total")
        for seg in segments:
            text = seg.get('text', '')
            audio_url = seg.get('audio_url', 'N/A')
            print(f"\n[Segment {seg.get('segment_index')}]")
            print(f"  Text ({len(text)} chars): {text[:100]}...")
            print(f"  Audio: {audio_url}")
    
    print(f"\n✅ Audio files count in DB: {audio_files_count}")
    
    # Check if text files exist
    import os
    from pathlib import Path
    
    project_dir = Path("projects/Comedy_Test")
    script_file = project_dir / "script.txt"
    segmented_file = project_dir / "script_segmented.txt"
    
    print(f"\n📁 File System Check:")
    print(f"  script.txt: {'✅ EXISTS' if script_file.exists() else '❌ MISSING'}")
    print(f"  script_segmented.txt: {'✅ EXISTS' if segmented_file.exists() else '❌ MISSING'}")
    print(f"  Audio files: {len(list(project_dir.glob('*.mp3')))} MP3 files found")

conn.close()

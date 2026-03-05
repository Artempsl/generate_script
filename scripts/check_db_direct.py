"""
Simple script to check latest execution JSON directly from DB.
"""
import asyncio
import asyncpg
import json


async def check_db():
    conn = await asyncpg.connect("postgresql://postgres:postgres@localhost/scripts_db")
    
    # Get latest execution
    row = await conn.fetchrow("""
        SELECT request_id, status, project_name, genre, language,
               char_count, duration, iteration_count, tokens_used_total,
               retrieved_sources_count, audio_files_count, segments_json
        FROM executions
        WHERE request_id = 'test-melodrama-final'
    """)
    
    await conn.close()
    
    if not row:
        print("No execution found")
        return
    
    print("=" * 80)
    print("FINAL JSON RESPONSE (from database)")
    print("=" * 80)
    print()
    
    segments = json.loads(row['segments_json']) if row['segments_json'] else []
    
    response = {
        "request_id": row['request_id'],
        "status": row['status'],
        "project_name": row['project_name'],
        "genre": row['genre'],
        "language": row['language'],
        "segments": segments,
        "audio_files_count": row['audio_files_count'],
        "char_count": row['char_count'],
        "duration_target": row['duration'],
        "iteration_count": row['iteration_count'],
        "tokens_used_total": row['tokens_used_total'],
        "retrieved_sources_count": row['retrieved_sources_count'],
        "reasoning_trace": "summary only"
    }
    
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 80)
    print("URL FORMAT VALIDATION")
    print("=" * 80)
    
    if segments:
        first_url = segments[0]['audio_url']
        print(f"\nFirst audio URL: {first_url}")
        
        if "/projects/" in first_url:
            print("✅ URL uses /projects/ path (CORRECT)")
        else:
            print("❌ URL uses wrong path")
        
        # Check all URLs
        print(f"\nAll {len(segments)} audio URLs:")
        for seg in segments[:3]:
            print(f"  Segment {seg['segment_index']}: {seg['audio_url']}")
        if len(segments) > 3:
            print(f"  ... and {len(segments) - 3} more")


if __name__ == "__main__":
    asyncio.run(check_db())

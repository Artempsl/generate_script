"""Quick check of segments in database."""
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.database import DatabaseManager


async def check():
    db = DatabaseManager()
    await db.initialize()
    
    # Find art4455667 project
    execution = await db.get_execution("art4455667")
    
    if not execution:
        print("Project not found")
        # Try to find by project_name
        import asyncpg
        conn = await asyncpg.connect("postgresql://postgres:postgres@localhost/scripts_db")
        rows = await conn.fetch("SELECT request_id, project_name, segments_json FROM executions WHERE project_name LIKE '%art%' ORDER BY created_at DESC LIMIT 3")
        
        for row in rows:
            print(f"\n{'='*80}")
            print(f"Request ID: {row['request_id']}")
            print(f"Project: {row['project_name']}")
            
            if row['segments_json']:
                segments = json.loads(row['segments_json'])
                print(f"Segments count: {len(segments)}")
                print("\nFirst 3 segments:")
                for i, seg in enumerate(segments[:3], 1):
                    print(f"\n  Segment {seg.get('segment_index', i)}:")
                    print(f"  Text: {seg.get('text', '')[:100]}...")
        
        await conn.close()
    else:
        print(f"Found: {execution.project_name}")
        print(f"Segments: {len(execution.segments)}")
        for seg in execution.segments[:3]:
            print(f"\n  Segment {seg.get('segment_index')}:")
            print(f"  Text: {seg.get('text', '')[:100]}...")
    
    await db.close()


asyncio.run(check())

import asyncio
import sys
import aiosqlite
from pathlib import Path
sys.path.insert(0, '.')

from agent.config import DATABASE_PATH

async def check_recent_executions():
    """Check all recent executions in database"""
    
    print("\n" + "="*80)
    print("DATABASE EXECUTIONS CHECK")
    print("="*80 + "\n")
    
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            # Get all executions
            query = """
                SELECT 
                    request_id,
                    project_name,
                    status,
                    created_at,
                    iteration_count
                FROM executions 
                ORDER BY created_at DESC 
                LIMIT 15
            """
            
            async with db.execute(query) as cursor:
                rows = await cursor.fetchall()
            
            if not rows:
                print("✗ No executions found in database\n")
                return
            
            print(f"Found {len(rows)} recent executions:\n")
            print(f"{'REQUEST_ID':<40} {'PROJECT_NAME':<30} {'STATUS':<10} {'TIME':<20}")
            print("-" * 100)
            
            for row in rows:
                request_id = row[0]
                project_name = row[1]
                status = row[2]
                created = row[3][:16] if row[3] else 'N/A'  # Just date/time portion
                iteration_count = row[4] if len(row) > 4 else 0
                
                # Truncate long values
                rid_display = request_id[:37] + '...' if len(request_id) > 40 else request_id
                proj_display = project_name[:27] + '...' if len(project_name) > 30 else project_name
                
                print(f"{rid_display:<40} {proj_display:<30} {status:<10} {created:<20}")
                
                # Show details for art4455667
                if 'art' in project_name.lower() or '4455667' in project_name:
                    print(f"  └─ Details: iterations={iteration_count}")
            
            print("\n" + "="*80)
            
            # Check for art4455667 specifically
            art_query = """
                SELECT request_id, project_name, created_at, status
                FROM executions 
                WHERE project_name LIKE '%art%' OR project_name LIKE '%4455667%'
                ORDER BY created_at DESC
            """
            async with db.execute(art_query) as cursor:
                art_rows = await cursor.fetchall()
            
            if art_rows:
                print(f"\nFound {len(art_rows)} execution(s) matching 'art4455667':")
                for row in art_rows:
                    print(f"  • {row[0][:50]}")
                    print(f"    Project: {row[1]}")
                    print(f"    Status: {row[3]}")
                    print(f"    Created: {row[2]}")
            else:
                print("\n✗ No executions found with 'art4455667' in project_name")
        
    except Exception as e:
        print(f"✗ Database error: {type(e).__name__}: {e}\n")

if __name__ == "__main__":
    asyncio.run(check_recent_executions())

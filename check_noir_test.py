"""Quick check for noir detective test completion."""
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

async def check_test():
    from agent.database import DatabaseManager
    
    db = DatabaseManager()
    await db.initialize()
    
    # Check for test-noir-* executions
    import aiosqlite
    async with aiosqlite.connect("agent.db") as conn:
        cursor = await conn.execute(
            "SELECT request_id, status, char_count, iteration_count, tokens_used_total "
            "FROM executions WHERE request_id LIKE 'test-noir-%' "
            "ORDER BY created_at DESC LIMIT 1"
        )
        result = await cursor.fetchone()
        
        if result:
            print(f"✓ Found test execution:")
            print(f"  Request ID: {result[0]}")
            print(f"  Status: {result[1]}")
            print(f"  Characters: {result[2]}")
            print(f"  Iterations: {result[3]}")
            print(f"  Tokens: {result[4]}")
            return True
        else:
            print("✗ No noir detective test found in database")
            return False
    
    await db.close()

if __name__ == "__main__":
    found = asyncio.run(check_test())
    sys.exit(0 if found else 1)

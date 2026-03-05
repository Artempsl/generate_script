"""Check database record for art4455667."""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.database import DatabaseManager


async def check_execution():
    db = DatabaseManager()
    await db.initialize()
    
    exec_record = await db.get_execution('art4455667')
    
    if exec_record:
        print("\n" + "=" * 80)
        print("DATABASE RECORD FOR art4455667")
        print("=" * 80)
        print(f"\n✓ Found execution:")
        print(f"  Status:            {exec_record.status}")
        print(f"  Script length:     {len(exec_record.script) if exec_record.script else 0} chars")
        print(f"  Segments:          {exec_record.segment_count}")
        print(f"  Audio files:       {exec_record.audio_files_count}")
        print(f"  Iterations:        {exec_record.iteration_count}")
        print(f"  Tokens total:      {exec_record.tokens_used_total:,}")
        print(f"  Sources retrieved: {exec_record.retrieved_sources_count}")
        print(f"  Char count:        {exec_record.char_count}")
        print(f"  Target chars:      {exec_record.target_chars}")
        print(f"  Validation:        {'✓ PASSED' if exec_record.char_count > 0 else '✗ FAILED'}")
        
        # Check reasoning trace
        if exec_record.reasoning_trace:
            print(f"\n  Reasoning steps:   {len(exec_record.reasoning_trace)}")
            print("\n  Steps executed:")
            for i, step in enumerate(exec_record.reasoning_trace[:10], 1):
                action = step.get('action', 'unknown')
                print(f"    {i}. {action}")
            if len(exec_record.reasoning_trace) > 10:
                print(f"    ... and {len(exec_record.reasoning_trace) - 10} more")
        
        # Check if Pinecone was used
        if exec_record.retrieved_sources_count > 0:
            print(f"\n  ✓ Pinecone retrieved: {exec_record.retrieved_sources_count} sources")
        else:
            print("\n  ✗ No Pinecone sources retrieved")
            
    else:
        print("\n✗ Execution not found in database")
    
    await db.close()


if __name__ == "__main__":
    asyncio.run(check_execution())

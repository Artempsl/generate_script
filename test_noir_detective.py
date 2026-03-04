"""
Test script for Noir Detective genre (2 minutes).

Tests:
- ReAct reasoning logic
- API optimizations (client reuse, temperature, max_tokens)
- Error handling and logging
"""

import asyncio
import sys
import json
import time
from pathlib import Path
from datetime import datetime, timezone

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from agent.models import ScriptRequestItem, create_initial_state
from agent.graph import execute_agent
from agent.database import DatabaseManager


async def test_noir_detective():
    """Test 2-minute noir detective script generation."""
    
    # Generate unique request ID
    timestamp = int(time.time())
    request_id = f"test-noir-{timestamp}"
    
    print("\n" + "=" * 80)
    print("NOIR DETECTIVE TEST (2 MINUTES)")
    print("=" * 80)
    print(f"Request ID: {request_id}")
    print(f"Genre: Noir Detective")
    print(f"Duration: 2 minutes")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 80 + "\n")
    
    # Create test request
    request_item = ScriptRequestItem(
        isValid=True,
        projectName="Noir Detective Test",
        genre="Noir Detective",
        storyIdea="A private detective receives a mysterious photograph of a woman who died 10 years ago, standing in yesterday's crowd",
        duration=2,
        request_id=request_id
    )
    
    # Create initial state
    print("→ Creating initial state...")
    initial_state = create_initial_state(request_item)
    print(f"  Language detected: {initial_state['language']}")
    print(f"  Target characters: {initial_state['target_chars']:,}")
    print()
    
    # Execute agent
    print("→ Executing agent graph...")
    start_time = time.time()
    
    try:
        final_state = await execute_agent(initial_state)
        elapsed = time.time() - start_time
        
        print(f"\n✓ Agent execution completed in {elapsed:.2f}s")
        print()
        
        # Check results
        if final_state.get('error'):
            print(f"✗ ERROR: {final_state['error']}")
            return None
        
        # Print summary
        print("=" * 80)
        print("RESULTS")
        print("=" * 80)
        print(f"Status: {'success' if final_state.get('script') else 'error'}")
        print(f"Character count: {final_state.get('char_count', 0):,}")
        print(f"Target characters: {final_state['target_chars']:,}")
        print(f"Iterations: {final_state.get('iteration', 0) + 1}")
        print(f"Tokens used: {final_state.get('tokens_used', 0):,}")
        print(f"Sources retrieved: {final_state.get('retrieved_sources_count', 0)}")
        print(f"Reasoning trace steps: {len(final_state.get('reasoning_trace', []))}")
        print(f"Validation passed: {final_state.get('validation_passed', False)}")
        print("=" * 80 + "\n")
        
        # Save to database
        print("→ Saving execution to database...")
        db_manager = DatabaseManager()
        await db_manager.initialize()
        
        from agent.database import Execution
        execution = Execution(
            request_id=request_id,
            status="success" if final_state.get('script') else "error",
            project_name=request_item.projectName,
            genre=request_item.genre,
            duration=request_item.duration,
            language=final_state['language'],
            outline=final_state.get('outline', ''),
            script=final_state.get('script', ''),
            char_count=final_state.get('char_count', 0),
            target_chars=final_state['target_chars'],
            iteration_count=final_state.get('iteration', 0) + 1,
            tokens_used_total=final_state.get('tokens_used', 0),
            retrieved_sources_count=final_state.get('retrieved_sources_count', 0),
            reasoning_trace=final_state.get('reasoning_trace', [])
        )
        
        await db_manager.save_execution(execution)
        await db_manager.close()
        
        print(f"✓ Execution saved to database")
        print(f"\nScript preview (first 500 chars):")
        print("-" * 80)
        script = final_state.get('script', '')
        print(script[:500] + "..." if len(script) > 500 else script)
        print("-" * 80 + "\n")
        
        return final_state
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n✗ Agent execution failed after {elapsed:.2f}s")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = asyncio.run(test_noir_detective())
    
    if result:
        print("\n" + "=" * 80)
        print("TEST COMPLETED SUCCESSFULLY ✅")
        print("=" * 80)
        sys.exit(0)
    else:
        print("\n" + "=" * 80)
        print("TEST FAILED ❌")
        print("=" * 80)
        sys.exit(1)

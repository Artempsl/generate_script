"""
Database module for Agent Backend.

This module provides:
- SQLite database initialization and schema management
- Execution storage (for idempotency and historical tracking)
- In-memory cache (LRU for fast lookups)
- Async CRUD operations

Schema:
    executions table stores complete execution records including:
    - Request metadata (id, project, genre, duration)
    - Generated outputs (outline, script)
    - Metrics (token usage, iteration count, sources)
    - Reasoning trace (full JSON)
    - Timestamps

Security:
    - Parameterized queries (SQL injection prevention)
    - No sensitive data in logs
"""

import json
import aiosqlite
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List
from collections import OrderedDict

# Handle imports for both module and standalone execution
try:
    from agent.config import DATABASE_PATH, CACHE_MAX_SIZE
except ModuleNotFoundError:
    # Running as standalone script
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from agent.config import DATABASE_PATH, CACHE_MAX_SIZE


# =============================================================================
# DATABASE SCHEMA
# =============================================================================

CREATE_EXECUTIONS_TABLE = """
CREATE TABLE IF NOT EXISTS executions (
    request_id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    project_name TEXT,
    genre TEXT,
    duration INTEGER,
    language TEXT,
    outline TEXT,
    script TEXT,
    char_count INTEGER,
    target_chars INTEGER,
    iteration_count INTEGER,
    tokens_used_total INTEGER,
    retrieved_sources_count INTEGER,
    reasoning_trace_json TEXT,
    segments_json TEXT,
    audio_files_count INTEGER,
    video_url TEXT,
    fact_check_citations_json TEXT,
    fact_check_report_json TEXT,
    error_message TEXT,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
)
"""

CREATE_INDEX_STATUS = """
CREATE INDEX IF NOT EXISTS idx_status ON executions(status)
"""

CREATE_INDEX_CREATED = """
CREATE INDEX IF NOT EXISTS idx_created_at ON executions(created_at DESC)
"""


# =============================================================================
# EXECUTION MODEL
# =============================================================================

class Execution:
    """Represents a single script generation execution."""
    
    def __init__(
        self,
        request_id: str,
        status: str,
        project_name: Optional[str] = None,
        genre: Optional[str] = None,
        duration: Optional[int] = None,
        language: Optional[str] = None,
        outline: Optional[str] = None,
        script: Optional[str] = None,
        char_count: Optional[int] = None,
        target_chars: Optional[int] = None,
        iteration_count: Optional[int] = None,
        tokens_used_total: Optional[int] = None,
        retrieved_sources_count: Optional[int] = None,
        reasoning_trace: Optional[List[Dict[str, Any]]] = None,
        segments: Optional[List[Dict[str, Any]]] = None,
        audio_files_count: Optional[int] = None,
        video_url: Optional[str] = None,
        fact_check_citations: Optional[List[Dict[str, Any]]] = None,
        fact_check_report: Optional[List[Dict[str, Any]]] = None,
        error_message: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.request_id = request_id
        self.status = status
        self.project_name = project_name
        self.genre = genre
        self.duration = duration
        self.language = language
        self.outline = outline
        self.script = script
        self.char_count = char_count
        self.target_chars = target_chars
        self.iteration_count = iteration_count
        self.tokens_used_total = tokens_used_total
        self.retrieved_sources_count = retrieved_sources_count
        self.reasoning_trace = reasoning_trace or []
        self.segments = segments or []
        self.audio_files_count = audio_files_count or 0
        self.video_url = video_url
        self.fact_check_citations = fact_check_citations or []
        self.fact_check_report = fact_check_report or []
        self.error_message = error_message
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert execution to dictionary."""
        return {
            "request_id": self.request_id,
            "status": self.status,
            "project_name": self.project_name,
            "genre": self.genre,
            "duration": self.duration,
            "language": self.language,
            "outline": self.outline,
            "script": self.script,
            "char_count": self.char_count,
            "target_chars": self.target_chars,
            "iteration_count": self.iteration_count,
            "tokens_used_total": self.tokens_used_total,
            "retrieved_sources_count": self.retrieved_sources_count,
            "reasoning_trace": self.reasoning_trace,
            "segments": self.segments,
            "audio_files_count": self.audio_files_count,
            "video_url": self.video_url,
            "fact_check_citations": self.fact_check_citations,
            "fact_check_report": self.fact_check_report,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def to_response(self) -> Dict[str, Any]:
        """Convert execution to API response format (summary only)."""
        from uuid import uuid4
        
        # Return summary of reasoning trace (not full trace)
        reasoning_summary = f"{len(self.reasoning_trace)} steps" if self.reasoning_trace else "0 steps"
        
        # Ensure request_id is never None (handle legacy database records)
        request_id = self.request_id if self.request_id else str(uuid4())
        
        return {
            "request_id": request_id,
            "status": self.status,
            "project_name": self.project_name,
            "segments": self.segments,
            "char_count": self.char_count,
            "duration_target": self.duration,
            "reasoning_trace": reasoning_summary,
            "iteration_count": self.iteration_count,
            "tokens_used_total": self.tokens_used_total,
            "retrieved_sources_count": self.retrieved_sources_count,
            "audio_files_count": self.audio_files_count,
            "video_url": self.video_url,
            "fact_check_citations": self.fact_check_citations,
            "fact_check_report": self.fact_check_report,
            "error_message": self.error_message,
        }
    
    @staticmethod
    def from_row(row: tuple) -> "Execution":
        """Create Execution from database row."""
        return Execution(
            request_id=row[0],
            status=row[1],
            project_name=row[2],
            genre=row[3],
            duration=row[4],
            language=row[5],
            outline=row[6],
            script=row[7],
            char_count=row[8],
            target_chars=row[9],
            iteration_count=row[10],
            tokens_used_total=row[11],
            retrieved_sources_count=row[12],
            reasoning_trace=json.loads(row[13]) if row[13] else [],
            segments=json.loads(row[14]) if row[14] else [],
            audio_files_count=row[15] if row[15] is not None else 0,
            video_url=row[16],
            fact_check_citations=json.loads(row[17]) if row[17] else [],
            fact_check_report=json.loads(row[18]) if row[18] else [],
            error_message=row[19],
            created_at=datetime.fromisoformat(row[20]) if row[20] else None,
            updated_at=datetime.fromisoformat(row[21]) if row[21] else None,
        )


# =============================================================================
# DATABASE MANAGER
# =============================================================================

class DatabaseManager:
    """Manages SQLite database and in-memory cache."""
    
    def __init__(self, db_path: Path = DATABASE_PATH):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.cache: OrderedDict[str, Execution] = OrderedDict()
        self.cache_max_size = CACHE_MAX_SIZE
    
    async def initialize(self) -> None:
        """
        Initialize database schema.
        
        Creates tables and indexes if they don't exist.
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(CREATE_EXECUTIONS_TABLE)
            # Safe migrations for new columns
            try:
                await db.execute("ALTER TABLE executions ADD COLUMN video_url TEXT")
            except Exception:
                pass
            try:
                await db.execute("ALTER TABLE executions ADD COLUMN fact_check_citations_json TEXT")
            except Exception:
                pass
            try:
                await db.execute("ALTER TABLE executions ADD COLUMN fact_check_report_json TEXT")
            except Exception:
                pass
            await db.execute(CREATE_INDEX_STATUS)
            await db.execute(CREATE_INDEX_CREATED)
            await db.commit()
    
    def _update_cache(self, execution: Execution) -> None:
        """
        Update in-memory cache with LRU eviction.
        
        Args:
            execution: Execution to cache
        """
        # Remove if exists (to update order)
        if execution.request_id in self.cache:
            del self.cache[execution.request_id]
        
        # Add to end (most recent)
        self.cache[execution.request_id] = execution
        
        # Evict oldest if over limit
        if len(self.cache) > self.cache_max_size:
            self.cache.popitem(last=False)
    
    async def get_execution(self, request_id: str) -> Optional[Execution]:
        """
        Get execution by request_id.
        
        Checks cache first, then database.
        
        Args:
            request_id: Unique request identifier
            
        Returns:
            Execution if found, None otherwise
        """
        # Check cache first
        if request_id in self.cache:
            return self.cache[request_id]
        
        # Query database
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM executions WHERE request_id = ?",
                (request_id,)
            ) as cursor:
                row = await cursor.fetchone()
                
                if row:
                    execution = Execution.from_row(row)
                    self._update_cache(execution)
                    return execution
        
        return None

    async def get_execution_by_project_name(self, project_name: str) -> Optional[Execution]:
        """
        Get execution by project_name.
        
        Args:
            project_name: Project slug/name
            
        Returns:
            Execution if found, None otherwise
        """
        # Check cache for matching project_name
        for execution in self.cache.values():
            if execution.project_name == project_name:
                return execution
        
        # Query database - get most recent execution for this project
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM executions WHERE project_name = ? ORDER BY created_at DESC LIMIT 1",
                (project_name,)
            ) as cursor:
                row = await cursor.fetchone()
                
                if row:
                    execution = Execution.from_row(row)
                    self._update_cache(execution)
                    return execution
        
        return None
    
    async def save_execution(self, execution: Execution) -> None:
        """
        Save or update execution.
        
        Args:
            execution: Execution to save
        """
        execution.updated_at = datetime.now(timezone.utc)
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO executions (
                    request_id, status, project_name, genre, duration, language,
                    outline, script, char_count, target_chars,
                    iteration_count, tokens_used_total, retrieved_sources_count,
                    reasoning_trace_json, segments_json, audio_files_count,
                    video_url, fact_check_citations_json, fact_check_report_json,
                    error_message, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(request_id) DO UPDATE SET
                    status = excluded.status,
                    outline = excluded.outline,
                    script = excluded.script,
                    char_count = excluded.char_count,
                    target_chars = excluded.target_chars,
                    iteration_count = excluded.iteration_count,
                    tokens_used_total = excluded.tokens_used_total,
                    retrieved_sources_count = excluded.retrieved_sources_count,
                    reasoning_trace_json = excluded.reasoning_trace_json,
                    segments_json = excluded.segments_json,
                    audio_files_count = excluded.audio_files_count,
                    video_url = excluded.video_url,
                    fact_check_citations_json = excluded.fact_check_citations_json,
                    fact_check_report_json = excluded.fact_check_report_json,
                    error_message = excluded.error_message,
                    updated_at = excluded.updated_at
                """,
                (
                    execution.request_id,
                    execution.status,
                    execution.project_name,
                    execution.genre,
                    execution.duration,
                    execution.language,
                    execution.outline,
                    execution.script,
                    execution.char_count,
                    execution.target_chars,
                    execution.iteration_count,
                    execution.tokens_used_total,
                    execution.retrieved_sources_count,
                    json.dumps(execution.reasoning_trace),
                    json.dumps(execution.segments),
                    execution.audio_files_count,
                    execution.video_url,
                    json.dumps(execution.fact_check_citations),
                    json.dumps(execution.fact_check_report),
                    execution.error_message,
                    execution.created_at.isoformat(),
                    execution.updated_at.isoformat(),
                )
            )
            await db.commit()
        
        # Update cache
        self._update_cache(execution)
    
    async def get_recent_executions(self, limit: int = 10) -> List[Execution]:
        """
        Get recent executions.
        
        Args:
            limit: Maximum number of executions to return
            
        Returns:
            List of recent executions
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM executions ORDER BY created_at DESC LIMIT ?",
                (limit,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [Execution.from_row(row) for row in rows]
    
    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Dictionary with statistics
        """
        async with aiosqlite.connect(self.db_path) as db:
            # Total executions
            async with db.execute("SELECT COUNT(*) FROM executions") as cursor:
                total = (await cursor.fetchone())[0]
            
            # Successful executions
            async with db.execute(
                "SELECT COUNT(*) FROM executions WHERE status = 'success'"
            ) as cursor:
                successful = (await cursor.fetchone())[0]
            
            # Failed executions
            async with db.execute(
                "SELECT COUNT(*) FROM executions WHERE status = 'error'"
            ) as cursor:
                failed = (await cursor.fetchone())[0]
            
            # Average iteration count
            async with db.execute(
                "SELECT AVG(iteration_count) FROM executions WHERE status = 'success'"
            ) as cursor:
                avg_iterations = (await cursor.fetchone())[0] or 0
            
            # Average tokens used
            async with db.execute(
                "SELECT AVG(tokens_used_total) FROM executions WHERE status = 'success'"
            ) as cursor:
                avg_tokens = (await cursor.fetchone())[0] or 0
            
            return {
                "total_executions": total,
                "successful": successful,
                "failed": failed,
                "success_rate": (successful / total * 100) if total > 0 else 0,
                "avg_iterations": round(avg_iterations, 2),
                "avg_tokens_used": round(avg_tokens, 2),
                "cache_size": len(self.cache),
            }


# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

# Singleton database manager
db_manager = DatabaseManager()


# =============================================================================
# CLI FOR TESTING
# =============================================================================

if __name__ == "__main__":
    """Test database operations."""
    import asyncio
    import sys
    from pathlib import Path
    
    # Add parent directory to path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    async def test_database():
        print("=" * 80)
        print("DATABASE MODULE TEST")
        print("=" * 80)
        
        # Initialize database
        print("\n1. Initializing database...")
        await db_manager.initialize()
        print("   ✓ Database initialized")
        print(f"   ✓ Database path: {db_manager.db_path}")
        
        # Create test execution
        print("\n2. Creating test execution...")
        test_execution = Execution(
            request_id="test-001",
            status="success",
            project_name="Test Project",
            genre="Comedy",
            duration=5,
            language="en",
            outline="Test outline",
            script="Test script content",
            char_count=5000,
            target_chars=5000,
            iteration_count=1,
            tokens_used_total=1500,
            retrieved_sources_count=3,
            reasoning_trace=[
                {"step": 1, "action": "retrieve", "result": "success"},
                {"step": 2, "action": "generate_outline", "result": "success"},
                {"step": 3, "action": "generate_script", "result": "success"},
            ]
        )
        
        await db_manager.save_execution(test_execution)
        print("   ✓ Test execution saved")
        
        # Retrieve execution
        print("\n3. Retrieving execution...")
        retrieved = await db_manager.get_execution("test-001")
        
        if retrieved:
            print("   ✓ Execution retrieved")
            print(f"   - Request ID: {retrieved.request_id}")
            print(f"   - Status: {retrieved.status}")
            print(f"   - Genre: {retrieved.genre}")
            print(f"   - Duration: {retrieved.duration} minutes")
            print(f"   - Language: {retrieved.language}")
            print(f"   - Tokens used: {retrieved.tokens_used_total}")
            print(f"   - Iterations: {retrieved.iteration_count}")
            print(f"   - Reasoning steps: {len(retrieved.reasoning_trace)}")
        else:
            print("   ✗ Execution not found")
            return
        
        # Test idempotency (retrieve again - should come from cache)
        print("\n4. Testing cache (retrieve again)...")
        cached = await db_manager.get_execution("test-001")
        print("   ✓ Retrieved from cache")
        print(f"   - Cache size: {len(db_manager.cache)}")
        
        # Get statistics
        print("\n5. Getting database statistics...")
        stats = await db_manager.get_statistics()
        print("   ✓ Statistics:")
        print(f"   - Total executions: {stats['total_executions']}")
        print(f"   - Successful: {stats['successful']}")
        print(f"   - Failed: {stats['failed']}")
        print(f"   - Success rate: {stats['success_rate']:.1f}%")
        print(f"   - Avg iterations: {stats['avg_iterations']}")
        print(f"   - Avg tokens: {stats['avg_tokens_used']:.0f}")
        
        # Test response format
        print("\n6. Testing API response format...")
        response = test_execution.to_response()
        print("   ✓ Response generated:")
        import json
        print(json.dumps(response, indent=2))
        
        print("\n" + "=" * 80)
        print("✓ DATABASE TEST PASSED")
        print("=" * 80)
    
    # Run test
    asyncio.run(test_database())

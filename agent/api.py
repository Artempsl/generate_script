"""
FastAPI Application for Agent Backend.

This module provides the REST API for n8n integration:
- POST /generate-script - Main endpoint for script generation
- GET /test - Test endpoint for health check

Architecture:
    Request → Validation → Database Check (idempotency) → Graph Execution 
          → Database Save → Response
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, List, Union
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError

# Handle both module and standalone execution
try:
    from agent.config import SERVER_PORT, MAX_TIMEOUT_SECONDS, validate_agent_environment
    from agent.models import (
        ScriptRequestItem,
        ScriptResponse,
        SegmentedScriptResponse,
        create_initial_state,
        create_teacher_initial_state,
        state_to_response,
        state_to_segmented_response
    )
    from agent.database import DatabaseManager, Execution
    from agent.graph import execute_agent
    from agent.teacher.graph import execute_teacher_agent
except ModuleNotFoundError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from agent.config import SERVER_PORT, MAX_TIMEOUT_SECONDS, validate_agent_environment
    from agent.models import (
        ScriptRequestItem,
        ScriptResponse,
        SegmentedScriptResponse,
        create_initial_state,
        create_teacher_initial_state,
        state_to_response,
        state_to_segmented_response
    )
    from agent.database import DatabaseManager, Execution
    from agent.graph import execute_agent
    from agent.teacher.graph import execute_teacher_agent


# =============================================================================
# LOGGING SETUP
# =============================================================================

logger = logging.getLogger(__name__)


# =============================================================================
# APPLICATION INITIALIZATION
# =============================================================================

app = FastAPI(
    title="Script Generation Agent Backend",
    description="Autonomous agent for storytelling script generation with Pinecone RAG",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for n8n integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # n8n can call from any origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for project outputs (audio + text files)
app.mount("/projects", StaticFiles(directory="projects"), name="projects")

# Initialize database manager
db_manager = DatabaseManager()


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def save_final_json_to_project(project_slug: str, response_data: Dict[str, Any]) -> None:
    """
    Save final n8n response JSON to project directory.
    
    Args:
        project_slug: URL-safe project name
        response_data: Complete response data to save
    """
    try:
        project_dir = Path("projects") / project_slug
        if not project_dir.exists():
            logger.warning(f"Project directory not found: {project_dir}")
            return
        
        json_path = project_dir / "final_response.json"
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(response_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✓ Final JSON saved to {json_path}")
    except Exception as e:
        logger.error(f"✗ Failed to save final JSON: {e}")


# =============================================================================
# EXCEPTION HANDLERS
# =============================================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom handler for Pydantic validation errors.
    Logs detailed error information for debugging.
    """
    # Log detailed error info
    logger.error("=" * 80)
    logger.error(f"VALIDATION ERROR - {request.method} {request.url.path}")
    logger.error(f"Client IP: {request.client.host if request.client else 'unknown'}")
    logger.error(f"Errors: {exc.errors()}")
    
    # Try to log request body
    try:
        body = await request.body()
        logger.error(f"Request body: {body.decode('utf-8')[:500]}")
    except:
        logger.error("Request body: <unable to read>")
    
    logger.error("=" * 80)
    
    # Return standard 422 response
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body}
    )


# =============================================================================
# STARTUP/SHUTDOWN EVENTS
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize database and validate environment on startup."""
    logger.info("=" * 80)
    logger.info("AGENT BACKEND STARTUP")
    logger.info("=" * 80)
    
    # Validate environment variables
    try:
        validate_agent_environment()
        logger.info("✓ Environment variables validated")
    except ValueError as e:
        logger.warning(f"✗ Environment validation failed: {e}")
        logger.warning("  Warning: Some features may not work correctly")
    
    # Initialize database
    await db_manager.initialize()
    logger.info("✓ Database initialized")
    
    logger.info(f"✓ Server ready on port {SERVER_PORT}")
    logger.info("=" * 80)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("=" * 80)
    logger.info("AGENT BACKEND SHUTDOWN")
    logger.info("=" * 80)
    # Database manager cleanup (connection pool auto-closes)
    logger.info("✓ Shutdown complete")
    logger.info("=" * 80)


# =============================================================================
# MIDDLEWARE
# =============================================================================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    start_time = datetime.now(timezone.utc)
    
    # Log request
    logger.info(f"→ {request.method} {request.url.path}")
    
    # Process request
    response = await call_next(request)
    
    # Log response time
    duration = (datetime.now(timezone.utc) - start_time).total_seconds()
    logger.info(f"← {response.status_code} ({duration:.2f}s)")
    
    return response


# =============================================================================
# ENDPOINTS
# =============================================================================

@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "service": "Script Generation Agent Backend",
        "version": "2.0.0",
        "status": "operational",
        "endpoints": {
            "generate": "POST /generate-script",
            "test": "GET /test",
            "docs": "GET /docs",
            "health": "GET /health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Check database connection
        stats = await db_manager.get_statistics()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "database": {
                "connected": True,
                "total_executions": stats.get("total_executions", 0)
            },
            "environment": {
                "OPENAI_API_KEY": "✓" if os.getenv("OPENAI_API_KEY") else "✗",
                "PINECONE_API_KEY": "✓" if os.getenv("PINECONE_API_KEY") else "✗",
                "COHERE_API_KEY": "✓" if os.getenv("COHERE_API_KEY") else "✗",
                "SERPAPI_API_KEY": "✓" if os.getenv("SERPAPI_API_KEY") else "✗ (optional)"
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


@app.get("/test")
async def test_endpoint():
    """
    Test endpoint for validation.
    
    Returns basic system information without executing agent.
    """
    return {
        "message": "Agent Backend Test Endpoint",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "config": {
            "port": SERVER_PORT,
            "max_iterations": 3,
            "max_tokens": 35000,
            "char_rate_russian": 1450,
            "char_rate_english": 1000
        },
        "environment": {
            "OPENAI_API_KEY": "set" if os.getenv("OPENAI_API_KEY") else "not set",
            "PINECONE_API_KEY": "set" if os.getenv("PINECONE_API_KEY") else "not set",
            "COHERE_API_KEY": "set" if os.getenv("COHERE_API_KEY") else "not set",
            "SERPAPI_API_KEY": "set" if os.getenv("SERPAPI_API_KEY") else "not set"
        }
    }


@app.post("/generate-script")
async def generate_script(request: Request):
    """
    Main endpoint for script generation.
    
    Accepts BOTH n8n formats:
    1. Array format (original): [{...}]
    2. Direct object (n8n default): {...}
    
    Supports BOTH field naming conventions:
    - camelCase: projectName, storyIdea
    - snake_case: project_name, story_idea (n8n default)
    
    Expected formats:
    
    Format 1 (Array):
    [
      {
        "isValid": true,
        "projectName": "string",  // or "project_name"
        "genre": "string",
        "storyIdea": "string",    // or "story_idea"
        "duration": 5
      }
    ]
    
    Format 2 (Direct object):
    {
      "project_name": "string",   // or "projectName"
      "genre": "string",
      "story_idea": "string",     // or "storyIdea"
      "duration": 5
    }
    
    Flow:
        1. Parse request body (auto-detect format)
        2. Validate request (Pydantic)
        3. Check database for existing execution (idempotency)
        4. Execute agent graph if new request
        5. Save execution to database
        6. Return response
    
    Args:
        request: FastAPI Request object
        
    Returns:
        ScriptResponse with script, outline, and metrics
        
    Raises:
        HTTPException: On validation or execution errors
    """
    try:
        from pydantic import ValidationError as PydanticValidationError
        # Parse raw body
        body = await request.body()
        body_str = body.decode('utf-8')
        body_json = json.loads(body_str)
        
        # Auto-detect format and extract item
        try:
            if isinstance(body_json, list):
                # Format 1: Array [{...}]
                if not body_json or len(body_json) == 0:
                    raise HTTPException(
                        status_code=422,
                        detail="Request array cannot be empty"
                    )
                request_item = ScriptRequestItem(**body_json[0])
                logger.debug(f"→ Detected array format: {len(body_json)} item(s)")
            elif isinstance(body_json, dict):
                # Format 2: Direct object {...}
                request_item = ScriptRequestItem(**body_json)
                logger.debug(f"→ Detected direct object format")
            else:
                raise HTTPException(
                    status_code=422,
                    detail="Invalid request format. Expected array [{...}] or object {...}"
                )
        except PydanticValidationError as ve:
            raise HTTPException(status_code=422, detail=str(ve))
        
        # Get request ID
        request_id = request_item.request_id
        
        logger.info("=" * 80)
        logger.info("SCRIPT GENERATION REQUEST")
        logger.info("=" * 80)
        logger.info(f"Request ID: {request_id}")
        logger.info(f"Project: {request_item.normalized_project_name}")
        logger.info(f"Genre/Topic: {request_item.genre or request_item.topic}")
        logger.info(f"Duration: {request_item.duration} min")
        logger.info(f"Idea: {request_item.normalized_story_idea[:100]}...")
        logger.info(f"Use case: {request_item.use_case}  |  Chat ID: {request_item.chat_id}")

        # ─── USE CASE ROUTING ─────────────────────────────────────────────────
        if request_item.use_case == "teacher":
            execute_fn = execute_teacher_agent
        elif request_item.use_case == "youtube":
            execute_fn = execute_agent
        else:
            raise HTTPException(
                status_code=422,
                detail=f"Unknown use_case: '{request_item.use_case}'. Supported values: 'youtube', 'teacher'"
            )
        # ──────────────────────────────────────────────────────────────────────

        # Check for existing execution (idempotency)
        existing = await db_manager.get_execution(request_id)
        if existing:
            logger.info("✓ Found existing execution (cached)")
            response = existing.to_response()
            # Always reflect current request's use_case/chat_id (not stored in DB)
            response["use_case"] = request_item.use_case
            response["chat_id"] = request_item.chat_id
            # For teacher pipeline, fact_check data is now stored in DB
            if request_item.use_case == "teacher":
                # fact_check_citations and fact_check_report already in response from DB
                pass
            logger.info("=" * 80)
            return JSONResponse(content=response)

        # Detect audio base URL from request headers
        host = request.headers.get("host", "localhost:8000")
        scheme = "https" if request.headers.get("x-forwarded-proto") == "https" else "http"
        audio_base_url = f"{scheme}://{host}"

        # Create initial state (routing-aware)
        logger.info("→ Creating initial state...")
        if request_item.use_case == "teacher":
            initial_state = create_teacher_initial_state(request_item)
        else:
            initial_state = create_initial_state(request_item)
        initial_state['audio_base_url'] = audio_base_url
        logger.info(f"  Language detected: {initial_state['language']}")
        logger.info(f"  Target characters: {initial_state['target_chars']:,}")
        logger.info(f"  Audio base URL: {audio_base_url}")
        
        # Execute agent graph with streaming keepalive to prevent Cloudflare 524
        logger.info(f"→ Executing agent graph (timeout: {MAX_TIMEOUT_SECONDS}s)...")

        async def _stream_response():
            # Start pipeline as independent task so keepalive loop doesn't block it
            pipeline_task = asyncio.create_task(
                asyncio.wait_for(execute_fn(initial_state), timeout=MAX_TIMEOUT_SECONDS)
            )

            # Send a space byte every 20s while pipeline runs — keeps Cloudflare alive
            while not pipeline_task.done():
                yield b" "
                try:
                    await asyncio.wait_for(asyncio.shield(pipeline_task), timeout=20)
                except asyncio.TimeoutError:
                    pass  # still running — loop again and send another keepalive

            # Pipeline finished — retrieve result
            try:
                final_state = pipeline_task.result()
            except asyncio.TimeoutError:
                error_msg = f"Agent execution timed out after {MAX_TIMEOUT_SECONDS}s"
                logger.error(f"✗ {error_msg}")
                yield json.dumps({"error": error_msg, "status": "error"}).encode()
                return
            except Exception as exc:
                error_msg = f"Agent execution failed: {exc}"
                logger.error(f"✗ {error_msg}")
                yield json.dumps({"error": error_msg, "status": "error"}).encode()
                return

            # Check for pipeline-level errors
            if final_state.get('error'):
                error_msg = final_state['error']
                logger.error(f"✗ Agent execution failed: {error_msg}")
                execution = Execution(
                    request_id=request_id,
                    status="error",
                    project_name=request_item.normalized_project_name,
                    genre=request_item.genre,
                    duration=request_item.duration,
                    language=final_state.get('language', initial_state['language']),
                    error_message=error_msg,
                    iteration_count=final_state.get('iteration', 0),
                    tokens_used_total=final_state.get('tokens_used', 0)
                )
                await db_manager.save_execution(execution)
                yield json.dumps({"error": error_msg, "status": "error"}).encode()
                return

            # Build response
            response = state_to_segmented_response(final_state)
            # Inject use_case/chat_id directly from request — guaranteed non-null
            response.use_case = request_item.use_case
            response.chat_id = request_item.chat_id

            logger.info("✓ Script generated successfully")
            logger.info(f"  Iterations: {final_state.get('iteration', 0) + 1}")
            logger.info(f"  Characters: {final_state.get('char_count', 0):,}")
            logger.info(f"  Tokens used: {final_state.get('tokens_used', 0):,}")
            logger.info(f"  Segments: {final_state.get('segment_count', 0)}")
            logger.info(f"  Audio files: {final_state.get('audio_files_count', 0)}")

            # Save to DB
            execution = Execution(
                request_id=request_id,
                status="success",
                project_name=request_item.normalized_project_name,
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
                reasoning_trace=final_state.get('reasoning_trace', []),
                segments=final_state.get('segments', []),
                audio_files_count=final_state.get('audio_files_count', 0),
                video_url=final_state.get('video_url'),
                fact_check_citations=final_state.get('fact_check_citations', []),
                fact_check_report=final_state.get('fact_check_snapshots', []),
            )
            await db_manager.save_execution(execution)
            logger.info("✓ Execution saved to database")
            
            # Save final JSON to project directory
            response_dict = response.model_dump()
            project_slug = final_state.get('project_slug', request_item.normalized_project_name)
            save_final_json_to_project(project_slug, response_dict)
            
            logger.info("=" * 80)

            yield response.model_dump_json().encode()

        return StreamingResponse(_stream_response(), media_type="application/json")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/executions/{request_id}")
async def get_execution(request_id: str):
    """
    Retrieve execution details by request_id.
    
    Args:
        request_id: Unique request identifier
        
    Returns:
        Execution details with full reasoning trace
    """
    execution = await db_manager.get_execution(request_id)
    
    if not execution:
        raise HTTPException(
            status_code=404,
            detail=f"Execution not found: {request_id}"
        )
    
    return execution.to_dict()


@app.get("/test-n8n-response/{project_name}")
async def test_n8n_response_get(project_name: str):
    """
    Test endpoint (GET): Returns existing project's final_response.json.
    Use this to preview what n8n will receive from /generate-script.
    
    Args:
        project_name: Project slug (e.g., Moon112121555777888999)
        
    Returns:
        Exact JSON that would be returned to n8n
    """
    project_file = Path(f"projects/{project_name}/final_response.json")
    
    if not project_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Project not found: {project_name}"
        )
    
    try:
        with open(project_file, "r", encoding="utf-8") as f:
            response_data = json.load(f)
        return response_data
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load project data: {str(e)}"
        )


@app.post("/test-n8n-response")
async def test_n8n_response_post(request: Request):
    """
    Test endpoint (POST): Accepts same format as /generate-script but returns 
    existing project data without generating anything. Perfect for testing n8n 
    integration without spending tokens.
    
    Request body should include project_name field.
    
    Returns:
        Exact JSON that n8n would receive from /generate-script
    """
    try:
        body = await request.json()
        project_name = body.get("project_name")
        
        if not project_name:
            raise HTTPException(
                status_code=400,
                detail="project_name is required in request body"
            )
        
        project_file = Path(f"projects/{project_name}/final_response.json")
        
        if not project_file.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Project not found: {project_name}"
            )
        
        with open(project_file, "r", encoding="utf-8") as f:
            response_data = json.load(f)
        
        logger.info(f"✓ Test response returned for project: {project_name}")
        return response_data
        
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON in request body"
        )
    except Exception as e:
        logger.error(f"Test endpoint error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load project data: {str(e)}"
        )


@app.get("/statistics")
async def get_statistics():
    """
    Get aggregate statistics across all executions.
    
    Returns:
        Statistics including success rate, average metrics, etc.
    """
    stats = await db_manager.get_statistics()
    return stats


# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for uncaught errors."""
    logger.error(f"✗ Uncaught exception: {exc}")
    import traceback
    traceback.print_exc()
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "path": str(request.url.path)
        }
    )


# =============================================================================
# MAIN (for testing)
# =============================================================================

if __name__ == "__main__":
    """Run server directly for testing."""
    import uvicorn
    
    logger.info("=" * 80)
    logger.info("STARTING AGENT BACKEND SERVER (TEST MODE)")
    logger.info("=" * 80)
    logger.info(f"Server will run on: http://0.0.0.0:{SERVER_PORT}")
    logger.info(f"API docs available at: http://localhost:{SERVER_PORT}/docs")
    logger.info(f"Test endpoint: http://localhost:{SERVER_PORT}/test")
    logger.info("=" * 80)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=SERVER_PORT,
        log_level="info"
    )

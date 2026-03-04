"""
Server Entry Point.

Launch the Agent Backend FastAPI server.
"""

import uvicorn
from agent.config import SERVER_PORT

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("AGENT BACKEND SERVER")
    print("=" * 80)
    print(f"Starting server on: http://0.0.0.0:{SERVER_PORT}")
    print(f"API documentation: http://localhost:{SERVER_PORT}/docs")
    print(f"Test endpoint: http://localhost:{SERVER_PORT}/test")
    print(f"Health check: http://localhost:{SERVER_PORT}/health")
    print("=" * 80 + "\n")
    
    uvicorn.run(
        "agent.api:app",
        host="0.0.0.0",
        port=SERVER_PORT,
        reload=False,  # Set to True for development
        log_level="info"
    )

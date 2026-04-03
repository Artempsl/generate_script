"""
Configuration module for Agent Backend (Phase 2).

This module centralizes all agent-specific configuration including:
- LLM settings (OpenAI GPT-4o-mini)
- Agent constraints (iterations, tokens, timeouts)
- Search settings (SerpAPI)
- Database paths
- Character rate mappings (RU/EN)

Security: All secrets must be loaded from Windows environment variables.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any


# =============================================================================
# PROJECT PATHS
# =============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
AGENT_DIR = PROJECT_ROOT / "agent"
LOGS_DIR = PROJECT_ROOT / "logs"
REPORTS_DIR = PROJECT_ROOT / "reports"
DATABASE_PATH = PROJECT_ROOT / "agent.db"

# Agent logs
AGENT_LOG_FILE = LOGS_DIR / "agent_logs.json"


# =============================================================================
# OPENAI CONFIGURATION
# =============================================================================

# Model selection: GPT-4o-mini for cost-effectiveness and quality balance
OPENAI_MODEL = "gpt-4o-mini"

# Temperature settings
OUTLINE_TEMPERATURE = 0.7  # Balanced creativity for structure
SCRIPT_TEMPERATURE = 0.8   # Higher creativity for storytelling

# Token limits
MAX_OUTLINE_TOKENS = 2000
MAX_SCRIPT_TOKENS_BASE = 10000  # Dynamic, adjusted per request
MAX_TOTAL_TOKENS = 35000


# =============================================================================
# AGENT CONSTRAINTS
# =============================================================================

MAX_ITERATIONS = 3
MAX_TIMEOUT_SECONDS = 3000  # 50 minutes total for long image+video pipelines

# Retry configuration
TOOL_MAX_RETRIES = 2
TOOL_RETRY_MIN_WAIT = 1  # seconds
TOOL_RETRY_MAX_WAIT = 10  # seconds


# =============================================================================
# PINECONE CONFIGURATION (reusing from Phase 1)
# =============================================================================

PINECONE_INDEX_NAME = "storytelling"
PINECONE_NAMESPACE = ""
PINECONE_TOP_K = 5  # Number of vectors to retrieve


# =============================================================================
# SERPAPI CONFIGURATION
# =============================================================================

# Web search only enabled for videos > 10 minutes
WEB_SEARCH_DURATION_THRESHOLD = 10  # minutes

# Search query template
SERPAPI_QUERY_TEMPLATE = "best storytelling practices 2026 for {genre}"

# Validation rules
SERPAPI_MIN_PUBLICATION_YEAR = 2025
SERPAPI_MIN_KEYWORD_MATCHES = 2
SERPAPI_TIMEOUT_SECONDS = 20


# =============================================================================
# LANGUAGE & CHARACTER RATE CONFIGURATION
# =============================================================================

# Characters per minute for different languages
CHAR_RATE_RUSSIAN = 1450
CHAR_RATE_ENGLISH = 1000

# Language detection threshold (Cyrillic ratio)
CYRILLIC_DETECTION_THRESHOLD = 0.3


# =============================================================================
# SCRIPT VALIDATION
# =============================================================================

# Script length tolerance (90% - 110% of target)
MIN_LENGTH_RATIO = 0.90
MAX_LENGTH_RATIO = 1.10


# =============================================================================
# FASTAPI SERVER CONFIGURATION
# =============================================================================

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8001
SERVER_RELOAD = False  # Set to True for development


# =============================================================================
# CACHE CONFIGURATION
# =============================================================================

# In-memory cache size (for idempotency)
CACHE_MAX_SIZE = 100


# =============================================================================
# EXTERNAL API CONFIGURATION
# =============================================================================

def _read_win_env(name: str) -> str:
    """
    Read an environment variable from the Windows registry (Machine + User scopes),
    falling back to os.getenv. This ensures the value is current even if the process
    was started before the variable was set in System Properties.
    """
    value = os.getenv(name, "")
    if value:
        return value
    try:
        import winreg
        for hive, subkey in [
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"),
            (winreg.HKEY_CURRENT_USER, r"Environment"),
        ]:
            try:
                with winreg.OpenKey(hive, subkey) as key:
                    val, _ = winreg.QueryValueEx(key, name)
                    if val:
                        return str(val)
            except FileNotFoundError:
                continue
    except Exception:
        pass
    return ""


FACTICITY_API = _read_win_env("FACTICITY_API")


# =============================================================================
# ENVIRONMENT VARIABLE VALIDATION
# =============================================================================

def validate_agent_environment() -> Dict[str, str]:
    """
    Validate that all required environment variables are set.
    
    Returns:
        Dict[str, str]: Dictionary of validated environment variables
        
    Raises:
        SystemExit: If any required variable is missing
    """
    required_vars = {
        "OPENAI_API_KEY": "OpenAI API key for GPT-4o-mini",
        "PINECONE_API_KEY": "Pinecone API key for vector database",
        "COHERE_API_KEY": "Cohere API key for embeddings",
        "SERPAPI_API_KEY": "SerpAPI key for web search (optional)",
        "FACTICITY_API": "Facticity API URL for teacher fact-checking (optional)",
    }
    
    missing_vars = []
    env_vars = {}
    optional_vars = ["SERPAPI_API_KEY", "FACTICITY_API"]
    
    for var_name, description in required_vars.items():
        value = os.environ.get(var_name)
        if not value and var_name not in optional_vars:
            missing_vars.append(f"  - {var_name}: {description}")
        elif value:
            env_vars[var_name] = value
    
    if missing_vars:
        print("❌ ERROR: Missing required environment variables:", file=sys.stderr)
        print("\n".join(missing_vars), file=sys.stderr)
        print("\nPlease set these as Windows environment variables.", file=sys.stderr)
        sys.exit(1)
    
    # Warn about optional variables
    if "SERPAPI_API_KEY" not in env_vars:
        print("⚠ Warning: SERPAPI_API_KEY not set. Web search will be disabled.", file=sys.stderr)
    
    return env_vars


def get_agent_config_summary() -> Dict[str, Any]:
    """
    Get a summary of current agent configuration (safe for logging).
    
    Returns:
        Dict[str, Any]: Configuration summary without secrets
    """
    return {
        "openai_model": OPENAI_MODEL,
        "max_iterations": MAX_ITERATIONS,
        "max_total_tokens": MAX_TOTAL_TOKENS,
        "max_outline_tokens": MAX_OUTLINE_TOKENS,
        "pinecone_index": PINECONE_INDEX_NAME,
        "pinecone_top_k": PINECONE_TOP_K,
        "web_search_threshold_minutes": WEB_SEARCH_DURATION_THRESHOLD,
        "char_rate_ru": CHAR_RATE_RUSSIAN,
        "char_rate_en": CHAR_RATE_ENGLISH,
        "validation_range": f"{MIN_LENGTH_RATIO}-{MAX_LENGTH_RATIO}",
        "server_port": SERVER_PORT,
    }


# =============================================================================
# INITIALIZATION
# =============================================================================

def initialize_agent_config() -> Dict[str, str]:
    """
    Initialize and validate all agent configuration.
    
    Returns:
        Dict[str, str]: Validated environment variables
    """
    # Ensure directories exist
    LOGS_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(exist_ok=True)
    
    # Validate environment variables
    env_vars = validate_agent_environment()
    
    return env_vars

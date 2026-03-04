"""
Configuration module for Pinecone ingestion pipeline.

This module centralizes all configuration constants and validates
required environment variables at runtime.

Security: All secrets must be loaded from Windows environment variables.
No hardcoded credentials allowed.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any


# =============================================================================
# PROJECT PATHS
# =============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"
SRC_DIR = PROJECT_ROOT / "src"

# Input PDF file path
PDF_FILE_PATH = Path(r"C:\Users\kupit\w5\generate_script\bestpractices.pdf")


# =============================================================================
# PINECONE CONFIGURATION
# =============================================================================

PINECONE_INDEX_NAME = "storytelling"
PINECONE_NAMESPACE = ""  # Default namespace
PINECONE_UPSERT_BATCH_SIZE = 100  # Optimal for serverless


# =============================================================================
# COHERE CONFIGURATION
# =============================================================================

COHERE_MODEL = "embed-english-v3.0"
COHERE_INPUT_TYPE = "search_document"  # For indexing documents
COHERE_EMBEDDING_DIMENSION = 1024  # Dimension for embed-english-v3.0
COHERE_BATCH_SIZE = 96  # Max texts per API call


# =============================================================================
# CHUNKING CONFIGURATION
# =============================================================================

# Target chunk size in tokens
# Justification: 600 tokens (~450 words) balances:
# - Retrieval granularity (precise enough for specific concepts)
# - Context completeness (enough context for understanding)
# - Embedding quality (within optimal range for Cohere)
CHUNK_TARGET_TOKENS = 600

# Chunk overlap in tokens
# Justification: 100 tokens (~17% overlap) ensures:
# - Context continuity across chunk boundaries
# - No loss of information at split points
# - Improved retrieval coherence for queries near boundaries
CHUNK_OVERLAP_TOKENS = 100

# Maximum deviation from target (prevents tiny final chunks)
CHUNK_MAX_TOKENS = 700

# Tokenizer for counting
# Justification: tiktoken cl100k_base is industry standard,
# deterministic, and widely used for embeddings
TOKENIZER_ENCODING = "cl100k_base"


# =============================================================================
# RETRY CONFIGURATION
# =============================================================================

MAX_RETRIES = 2
RETRY_INITIAL_DELAY = 1.0  # seconds
RETRY_BACKOFF_FACTOR = 2.0  # exponential backoff


# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

LOG_FILE_PATH = LOGS_DIR / "pinecone_ingestion_log.json"
LOG_PREVIEW_LENGTH = 200  # Characters to include in text preview


# =============================================================================
# ENVIRONMENT VARIABLE VALIDATION
# =============================================================================

def validate_environment() -> Dict[str, str]:
    """
    Validate that all required environment variables are set.
    
    Returns:
        Dict[str, str]: Dictionary of validated environment variables
        
    Raises:
        SystemExit: If any required variable is missing
    """
    required_vars = {
        "COHERE_API_KEY": "Cohere API key for embedding generation",
        "PINECONE_API_KEY": "Pinecone API key for vector database access",
    }
    
    missing_vars = []
    env_vars = {}
    
    for var_name, description in required_vars.items():
        value = os.environ.get(var_name)
        if not value:
            missing_vars.append(f"  - {var_name}: {description}")
        else:
            env_vars[var_name] = value
    
    if missing_vars:
        print("❌ ERROR: Missing required environment variables:", file=sys.stderr)
        print("\n".join(missing_vars), file=sys.stderr)
        print("\nPlease set these as Windows environment variables.", file=sys.stderr)
        sys.exit(1)
    
    return env_vars


def validate_pdf_exists() -> None:
    """
    Validate that the input PDF file exists.
    
    Raises:
        SystemExit: If PDF file does not exist
    """
    if not PDF_FILE_PATH.exists():
        print(f"❌ ERROR: PDF file not found: {PDF_FILE_PATH}", file=sys.stderr)
        sys.exit(1)


def get_config_summary() -> Dict[str, Any]:
    """
    Get a summary of current configuration (safe for logging).
    
    Returns:
        Dict[str, Any]: Configuration summary without secrets
    """
    return {
        "pinecone_index": PINECONE_INDEX_NAME,
        "cohere_model": COHERE_MODEL,
        "embedding_dimension": COHERE_EMBEDDING_DIMENSION,
        "chunk_target_tokens": CHUNK_TARGET_TOKENS,
        "chunk_overlap_tokens": CHUNK_OVERLAP_TOKENS,
        "tokenizer": TOKENIZER_ENCODING,
        "pdf_file": str(PDF_FILE_PATH),
    }


# =============================================================================
# INITIALIZATION
# =============================================================================

def initialize_config() -> Dict[str, str]:
    """
    Initialize and validate all configuration.
    
    Returns:
        Dict[str, str]: Validated environment variables
    """
    # Ensure log directory exists
    LOGS_DIR.mkdir(exist_ok=True)
    
    # Validate environment variables
    env_vars = validate_environment()
    
    # Validate PDF exists
    validate_pdf_exists()
    
    return env_vars

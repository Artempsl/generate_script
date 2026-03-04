"""
Cohere embedding generation module.

This module provides functionality to generate embeddings using the Cohere API
with batching, retry logic, and proper error handling.

Key features:
- Batch embedding requests (up to 96 texts per API call)
- Exponential backoff retry logic for transient failures
- Proper error handling and logging
- Validation of embedding dimensions
- API latency tracking
"""

import os
import sys
import time
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

try:
    import cohere
except ImportError:
    print("❌ ERROR: cohere not installed. Run: pip install cohere", file=sys.stderr)
    sys.exit(1)

from config import (
    COHERE_MODEL,
    COHERE_INPUT_TYPE,
    COHERE_EMBEDDING_DIMENSION,
    COHERE_BATCH_SIZE,
    MAX_RETRIES,
    RETRY_INITIAL_DELAY,
    RETRY_BACKOFF_FACTOR,
)


@dataclass
class EmbeddingResult:
    """Result of embedding generation for a batch."""
    embeddings: List[List[float]]
    num_texts: int
    dimension: int
    batch_number: int
    api_latency_seconds: float
    success: bool
    error_message: str = ""


class CohereEmbedder:
    """Cohere embedding client with batching and retry logic."""
    
    def __init__(self, api_key: str):
        """
        Initialize Cohere client.
        
        Args:
            api_key: Cohere API key
        """
        if not api_key:
            raise ValueError("Cohere API key is required")
        
        self.client = cohere.ClientV2(api_key=api_key)
        self.model = COHERE_MODEL
        self.input_type = COHERE_INPUT_TYPE
        self.expected_dimension = COHERE_EMBEDDING_DIMENSION
        self.batch_size = COHERE_BATCH_SIZE
    
    def _embed_with_retry(
        self,
        texts: List[str],
        batch_number: int,
        max_retries: int = MAX_RETRIES,
    ) -> EmbeddingResult:
        """
        Generate embeddings with retry logic.
        
        Args:
            texts: List of texts to embed
            batch_number: Batch identifier for logging
            max_retries: Maximum number of retry attempts
            
        Returns:
            EmbeddingResult: Result containing embeddings or error
        """
        delay = RETRY_INITIAL_DELAY
        
        for attempt in range(max_retries + 1):
            try:
                start_time = time.time()
                
                # Call Cohere API
                response = self.client.embed(
                    texts=texts,
                    model=self.model,
                    input_type=self.input_type,
                    embedding_types=["float"]
                )
                
                api_latency = time.time() - start_time
                
                # Extract embeddings
                embeddings = response.embeddings.float_
                
                # Validate dimensions
                if embeddings and len(embeddings[0]) != self.expected_dimension:
                    error_msg = (
                        f"Unexpected embedding dimension: {len(embeddings[0])} "
                        f"(expected {self.expected_dimension})"
                    )
                    return EmbeddingResult(
                        embeddings=[],
                        num_texts=len(texts),
                        dimension=len(embeddings[0]) if embeddings else 0,
                        batch_number=batch_number,
                        api_latency_seconds=api_latency,
                        success=False,
                        error_message=error_msg,
                    )
                
                return EmbeddingResult(
                    embeddings=embeddings,
                    num_texts=len(texts),
                    dimension=len(embeddings[0]) if embeddings else 0,
                    batch_number=batch_number,
                    api_latency_seconds=api_latency,
                    success=True,
                )
            
            except cohere.errors.TooManyRequestsError as e:
                if attempt < max_retries:
                    print(f"⚠ Rate limit hit on batch {batch_number}, retrying in {delay}s...", file=sys.stderr)
                    time.sleep(delay)
                    delay *= RETRY_BACKOFF_FACTOR
                else:
                    return EmbeddingResult(
                        embeddings=[],
                        num_texts=len(texts),
                        dimension=0,
                        batch_number=batch_number,
                        api_latency_seconds=0,
                        success=False,
                        error_message=f"Rate limit exceeded after {max_retries} retries: {e}",
                    )
            
            except cohere.errors.ServiceUnavailableError as e:
                if attempt < max_retries:
                    print(f"⚠ Service unavailable for batch {batch_number}, retrying in {delay}s...", file=sys.stderr)
                    time.sleep(delay)
                    delay *= RETRY_BACKOFF_FACTOR
                else:
                    return EmbeddingResult(
                        embeddings=[],
                        num_texts=len(texts),
                        dimension=0,
                        batch_number=batch_number,
                        api_latency_seconds=0,
                        success=False,
                        error_message=f"Service unavailable after {max_retries} retries: {e}",
                    )
            
            except Exception as e:
                # For other errors, don't retry
                return EmbeddingResult(
                    embeddings=[],
                    num_texts=len(texts),
                    dimension=0,
                    batch_number=batch_number,
                    api_latency_seconds=0,
                    success=False,
                    error_message=f"Embedding generation failed: {type(e).__name__}: {e}",
                )
        
        # Should never reach here
        return EmbeddingResult(
            embeddings=[],
            num_texts=len(texts),
            dimension=0,
            batch_number=batch_number,
            api_latency_seconds=0,
            success=False,
            error_message="Max retries exceeded",
        )
    
    def embed_chunks(self, texts: List[str]) -> Tuple[List[List[float]], List[Dict[str, Any]]]:
        """
        Generate embeddings for multiple texts with batching.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            Tuple containing:
                - List of embeddings (one per text)
                - List of batch metadata dictionaries
            
        Raises:
            RuntimeError: If any batch fails after retries
        """
        if not texts:
            return [], []
        
        all_embeddings = []
        batch_metadata = []
        total_batches = (len(texts) + self.batch_size - 1) // self.batch_size
        
        print(f"Generating embeddings for {len(texts)} texts in {total_batches} batch(es)...")
        
        for i in range(0, len(texts), self.batch_size):
            batch_texts = texts[i:i + self.batch_size]
            batch_number = i // self.batch_size
            
            print(f"  Processing batch {batch_number + 1}/{total_batches} ({len(batch_texts)} texts)...", end=" ")
            
            result = self._embed_with_retry(batch_texts, batch_number)
            
            if not result.success:
                print(f"❌ FAILED")
                error_msg = f"Batch {batch_number} failed: {result.error_message}"
                raise RuntimeError(error_msg)
            
            print(f"✓ ({result.api_latency_seconds:.2f}s)")
            
            all_embeddings.extend(result.embeddings)
            
            batch_metadata.append({
                "batch_number": batch_number,
                "num_texts": result.num_texts,
                "dimension": result.dimension,
                "api_latency_seconds": result.api_latency_seconds,
                "success": result.success,
            })
        
        print(f"✓ Generated {len(all_embeddings)} embeddings successfully")
        
        return all_embeddings, batch_metadata


def create_embedder(api_key: str = None) -> CohereEmbedder:
    """
    Create a Cohere embedder instance.
    
    Args:
        api_key: Cohere API key (if None, reads from environment)
        
    Returns:
        CohereEmbedder: Configured embedder instance
        
    Raises:
        ValueError: If API key is not provided or found in environment
    """
    if api_key is None:
        api_key = os.environ.get("COHERE_API_KEY")
    
    if not api_key:
        raise ValueError(
            "Cohere API key not found. Set COHERE_API_KEY environment variable."
        )
    
    return CohereEmbedder(api_key)


# =============================================================================
# CLI FOR TESTING
# =============================================================================

if __name__ == "__main__":
    """Test embedding generation from command line."""
    import sys
    sys.path.insert(0, '.')
    
    from src.pdf_extractor import extract_and_validate_pdf
    from src.config import PDF_FILE_PATH, initialize_config
    from src.chunker import chunk_text
    
    print("=" * 80)
    print("COHERE EMBEDDING GENERATION TEST")
    print("=" * 80)
    
    # Initialize configuration
    print("\n1. Initializing configuration...")
    env_vars = initialize_config()
    print("   ✓ Configuration validated")
    
    # Extract and chunk text
    print(f"\n2. Extracting and chunking PDF: {PDF_FILE_PATH.name}")
    text = extract_and_validate_pdf(PDF_FILE_PATH)
    chunks = chunk_text(text)
    print(f"   ✓ Created {len(chunks)} chunks")
    
    # Create embedder
    print(f"\n3. Creating Cohere embedder (model: {COHERE_MODEL})...")
    embedder = create_embedder()
    print(f"   ✓ Embedder initialized")
    print(f"   - Expected dimension: {COHERE_EMBEDDING_DIMENSION}")
    print(f"   - Batch size: {COHERE_BATCH_SIZE}")
    
    # Generate embeddings
    print(f"\n4. Generating embeddings for {len(chunks)} chunks...")
    try:
        chunk_texts = [chunk.text for chunk in chunks]
        embeddings, metadata = embedder.embed_chunks(chunk_texts)
        
        print(f"\n5. Validation:")
        print(f"   ✓ Total embeddings: {len(embeddings)}")
        print(f"   ✓ Embedding dimension: {len(embeddings[0]) if embeddings else 0}")
        print(f"   ✓ Total batches: {len(metadata)}")
        
        total_latency = sum(m["api_latency_seconds"] for m in metadata)
        print(f"   ✓ Total API latency: {total_latency:.2f}s")
        print(f"   ✓ Avg latency per batch: {total_latency / len(metadata):.2f}s")
        
        # Sample embedding
        if embeddings:
            print(f"\n6. Sample embedding (first 10 dimensions):")
            print(f"   {embeddings[0][:10]}")
        
        print("\n" + "=" * 80)
        print("✓ EMBEDDING GENERATION TEST PASSED")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

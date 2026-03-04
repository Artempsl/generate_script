"""
Main orchestration script for Pinecone ingestion pipeline.

This script coordinates the entire ingestion process:
1. Configuration validation
2. PDF text extraction
3. Deterministic text chunking
4. Cohere embedding generation
5. Pinecone vector upsert
6. Structured logging

Usage:
    python main.py

Environment variables required:
    - COHERE_API_KEY
    - PINECONE_API_KEY
"""

import sys
import time
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config import (
    initialize_config,
    get_config_summary,
    PDF_FILE_PATH,
    PINECONE_INDEX_NAME,
    COHERE_EMBEDDING_DIMENSION,
)
from pdf_extractor import extract_and_validate_pdf
from chunker import chunk_text, get_chunks_summary
from embedder import create_embedder
from pinecone_client import create_pinecone_client
from logger import create_logger


def print_header(title: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_section(title: str) -> None:
    """Print a section title."""
    print(f"\n{title}")
    print("-" * 80)


def main() -> int:
    """
    Main entry point for ingestion pipeline.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    pipeline_start_time = time.time()
    
    print_header("PINECONE INGESTION PIPELINE")
    print("Storytelling Best Practices Knowledge Base")
    print("Phase 1: Autonomous Ingestion Module")
    
    try:
        # =================================================================
        # STAGE 1: CONFIGURATION & INITIALIZATION
        # =================================================================
        print_section("Stage 1: Configuration & Initialization")
        
        env_vars = initialize_config()
        config_summary = get_config_summary()
        
        print("✓ Environment variables validated")
        print(f"  - COHERE_API_KEY: {'*' * 8}")
        print(f"  - PINECONE_API_KEY: {'*' * 8}")
        print(f"✓ Configuration loaded")
        print(f"  - Pinecone index: {config_summary['pinecone_index']}")
        print(f"  - Cohere model: {config_summary['cohere_model']}")
        print(f"  - Embedding dimension: {config_summary['embedding_dimension']}")
        print(f"  - Chunk target: {config_summary['chunk_target_tokens']} tokens")
        print(f"  - Chunk overlap: {config_summary['chunk_overlap_tokens']} tokens")
        print(f"  - PDF file: {PDF_FILE_PATH.name}")
        
        # Initialize logger
        logger = create_logger()
        logger.log_pipeline_start(config_summary)
        
        # =================================================================
        # STAGE 2: PDF TEXT EXTRACTION
        # =================================================================
        print_section("Stage 2: PDF Text Extraction")
        
        print(f"Extracting text from: {PDF_FILE_PATH}")
        text = extract_and_validate_pdf(PDF_FILE_PATH)
        
        word_count = len(text.split())
        char_count = len(text)
        
        print(f"✓ Text extracted successfully")
        print(f"  - Characters: {char_count:,}")
        print(f"  - Words: {word_count:,}")
        
        logger.log_pdf_extraction(
            file_path=str(PDF_FILE_PATH),
            word_count=word_count,
            char_count=char_count,
        )
        
        # =================================================================
        # STAGE 3: DETERMINISTIC CHUNKING
        # =================================================================
        print_section("Stage 3: Deterministic Text Chunking")
        
        print("Chunking text with sentence boundary preservation...")
        chunks = chunk_text(text)
        chunks_summary = get_chunks_summary(chunks)
        
        print(f"✓ Text chunked successfully")
        print(f"  - Total chunks: {chunks_summary['total_chunks']}")
        print(f"  - Total tokens: {chunks_summary['total_tokens']}")
        print(f"  - Avg tokens/chunk: {chunks_summary['avg_tokens_per_chunk']:.1f}")
        print(f"  - Min tokens: {chunks_summary['min_tokens']}")
        print(f"  - Max tokens: {chunks_summary['max_tokens']}")
        
        logger.log_chunking(
            num_chunks=chunks_summary['total_chunks'],
            total_tokens=chunks_summary['total_tokens'],
            avg_tokens=chunks_summary['avg_tokens_per_chunk'],
        )
        
        # Log individual chunks
        for chunk in chunks:
            text_preview = chunk.text[:200].replace('\n', ' ')
            logger.log_chunk(
                chunk_id=chunk.chunk_id,
                text_preview=text_preview,
                token_count=chunk.token_count,
            )
        
        # =================================================================
        # STAGE 4: COHERE EMBEDDING GENERATION
        # =================================================================
        print_section("Stage 4: Cohere Embedding Generation")
        
        embedder = create_embedder()
        chunk_texts = [chunk.text for chunk in chunks]
        
        embeddings, embedding_metadata = embedder.embed_chunks(chunk_texts)
        
        print(f"✓ Embeddings generated successfully")
        print(f"  - Total embeddings: {len(embeddings)}")
        print(f"  - Embedding dimension: {len(embeddings[0])}")
        print(f"  - Total batches: {len(embedding_metadata)}")
        
        # Log embedding batches
        for batch_meta in embedding_metadata:
            logger.log_embedding_batch(
                batch_number=batch_meta['batch_number'],
                num_texts=batch_meta['num_texts'],
                dimension=batch_meta['dimension'],
                latency=batch_meta['api_latency_seconds'],
            )
        
        total_embedding_latency = sum(m['api_latency_seconds'] for m in embedding_metadata)
        logger.log_embedding_summary(
            total_embeddings=len(embeddings),
            total_batches=len(embedding_metadata),
            total_latency=total_embedding_latency,
        )
        
        # =================================================================
        # STAGE 5: PINECONE VECTOR UPSERT
        # =================================================================
        print_section("Stage 5: Pinecone Vector Upsert")
        
        pc_client = create_pinecone_client()
        print(f"✓ Connected to Pinecone index: {PINECONE_INDEX_NAME}")
        
        pc_client.validate_index_dimension()
        print(f"✓ Index dimension validated")
        
        chunk_ids = [chunk.chunk_id for chunk in chunks]
        source_file = PDF_FILE_PATH.name
        
        upserted, skipped, upsert_metadata = pc_client.upsert_chunks(
            chunk_ids=chunk_ids,
            embeddings=embeddings,
            texts=chunk_texts,
            source_file=source_file,
            skip_existing=True,
        )
        
        print(f"✓ Upsert completed")
        print(f"  - Vectors upserted: {upserted}")
        print(f"  - Vectors skipped: {skipped}")
        print(f"  - Total batches: {len(upsert_metadata)}")
        
        # Log upsert batches
        for batch_meta in upsert_metadata:
            logger.log_upsert_batch(
                batch_number=batch_meta['batch_number'],
                num_vectors=batch_meta['num_vectors'],
            )
        
        logger.log_upsert_summary(
            total_upserted=upserted,
            total_skipped=skipped,
            total_batches=len(upsert_metadata),
        )
        
        # =================================================================
        # PIPELINE COMPLETION
        # =================================================================
        pipeline_end_time = time.time()
        execution_time = pipeline_end_time - pipeline_start_time
        
        # Create final summary
        summary = {
            "index_name": PINECONE_INDEX_NAME,
            "chunks_created": len(chunks),
            "embeddings_upserted": upserted,
            "embeddings_skipped": skipped,
            "embedding_dimension": COHERE_EMBEDDING_DIMENSION,
            "status": "success",
            "execution_time_seconds": round(execution_time, 2),
        }
        
        logger.log_pipeline_complete(summary)
        
        # Print final summary
        print_header("INGESTION COMPLETE")
        print("\nPipeline Summary:")
        print(f"  Chunks created: {summary['chunks_created']}")
        print(f"  Embeddings generated: {summary['chunks_created']}")
        print(f"  Upserts successful: {summary['embeddings_upserted']}")
        print(f"  Vectors skipped (existing): {summary['embeddings_skipped']}")
        print(f"  Execution time: {summary['execution_time_seconds']} seconds")
        print(f"  Status: {summary['status']}")
        
        print("\nFinal Summary JSON:")
        print(json.dumps(summary, indent=2))
        
        print("\n" + "=" * 80)
        print("✓ ALL STAGES COMPLETED SUCCESSFULLY")
        print("=" * 80)
        
        return 0
    
    except KeyboardInterrupt:
        print("\n\n⚠ Pipeline interrupted by user", file=sys.stderr)
        logger.error("pipeline_interrupted", "Pipeline interrupted by user")
        return 1
    
    except Exception as e:
        print("\n\n❌ PIPELINE FAILED", file=sys.stderr)
        print(f"Error: {e}", file=sys.stderr)
        
        import traceback
        traceback.print_exc()
        
        logger.log_pipeline_error(str(e), "unknown")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())

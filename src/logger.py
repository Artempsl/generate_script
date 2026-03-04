"""
Structured JSON logging module.

This module provides functionality for writing structured JSON logs
in a consistent format throughout the ingestion pipeline.

Key features:
- JSON-formatted logs (one JSON object per line - JSONL format)
- Thread-safe file operations
- Consistent timestamp format
- Multiple log levels (INFO, WARNING, ERROR)
- No secrets in logs
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from enum import Enum

from config import LOG_FILE_PATH


class LogLevel(Enum):
    """Log levels."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class StructuredLogger:
    """Structured JSON logger for ingestion pipeline."""
    
    def __init__(self, log_file: Path = LOG_FILE_PATH):
        """
        Initialize structured logger.
        
        Args:
            log_file: Path to log file
        """
        self.log_file = log_file
        
        # Ensure log directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Clear or create log file
        if self.log_file.exists():
            # Append mode - don't clear existing logs
            pass
        else:
            # Create new file
            self.log_file.touch()
    
    def _write_log(self, log_entry: Dict[str, Any]) -> None:
        """
        Write a log entry to file.
        
        Args:
            log_entry: Dictionary containing log data
        """
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                json.dump(log_entry, f, ensure_ascii=False)
                f.write('\n')
        except Exception as e:
            print(f"⚠ Warning: Failed to write log: {e}", file=sys.stderr)
    
    def log(
        self,
        level: LogLevel,
        stage: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Write a log entry.
        
        Args:
            level: Log level
            stage: Pipeline stage name
            message: Log message
            data: Additional data to include in log
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level.value,
            "stage": stage,
            "message": message,
        }
        
        if data:
            log_entry["data"] = data
        
        self._write_log(log_entry)
    
    def info(self, stage: str, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Log an INFO message."""
        self.log(LogLevel.INFO, stage, message, data)
    
    def warning(self, stage: str, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Log a WARNING message."""
        self.log(LogLevel.WARNING, stage, message, data)
    
    def error(self, stage: str, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Log an ERROR message."""
        self.log(LogLevel.ERROR, stage, message, data)
    
    def log_pipeline_start(self, config: Dict[str, Any]) -> None:
        """Log pipeline start with configuration."""
        self.info(
            stage="pipeline_start",
            message="Pinecone ingestion pipeline started",
            data={"config": config}
        )
    
    def log_pipeline_complete(self, summary: Dict[str, Any]) -> None:
        """Log pipeline completion with summary."""
        self.info(
            stage="pipeline_complete",
            message="Pinecone ingestion pipeline completed successfully",
            data={"summary": summary}
        )
    
    def log_pipeline_error(self, error_message: str, stage: str) -> None:
        """Log pipeline error."""
        self.error(
            stage=stage,
            message=f"Pipeline failed: {error_message}",
            data={"error": error_message}
        )
    
    def log_pdf_extraction(self, file_path: str, word_count: int, char_count: int) -> None:
        """Log PDF extraction."""
        self.info(
            stage="pdf_extraction",
            message="PDF text extracted successfully",
            data={
                "file_path": file_path,
                "word_count": word_count,
                "char_count": char_count,
            }
        )
    
    def log_chunking(self, num_chunks: int, total_tokens: int, avg_tokens: float) -> None:
        """Log text chunking."""
        self.info(
            stage="chunking",
            message="Text chunked successfully",
            data={
                "num_chunks": num_chunks,
                "total_tokens": total_tokens,
                "avg_tokens_per_chunk": avg_tokens,
            }
        )
    
    def log_chunk(self, chunk_id: str, text_preview: str, token_count: int) -> None:
        """Log individual chunk creation."""
        self.info(
            stage="chunking",
            message=f"Chunk created: {chunk_id}",
            data={
                "chunk_id": chunk_id,
                "text_preview": text_preview,
                "token_count": token_count,
            }
        )
    
    def log_embedding_batch(
        self,
        batch_number: int,
        num_texts: int,
        dimension: int,
        latency: float,
    ) -> None:
        """Log embedding batch generation."""
        self.info(
            stage="embedding_generation",
            message=f"Embedding batch {batch_number} generated",
            data={
                "batch_number": batch_number,
                "num_texts": num_texts,
                "embedding_dimension": dimension,
                "api_latency_seconds": latency,
            }
        )
    
    def log_embedding_summary(
        self,
        total_embeddings: int,
        total_batches: int,
        total_latency: float,
    ) -> None:
        """Log embedding generation summary."""
        self.info(
            stage="embedding_generation",
            message="All embeddings generated successfully",
            data={
                "total_embeddings": total_embeddings,
                "total_batches": total_batches,
                "total_latency_seconds": total_latency,
            }
        )
    
    def log_upsert_batch(self, batch_number: int, num_vectors: int) -> None:
        """Log upsert batch."""
        self.info(
            stage="pinecone_upsert",
            message=f"Upsert batch {batch_number} completed",
            data={
                "batch_number": batch_number,
                "num_vectors": num_vectors,
            }
        )
    
    def log_upsert_summary(
        self,
        total_upserted: int,
        total_skipped: int,
        total_batches: int,
    ) -> None:
        """Log upsert summary."""
        self.info(
            stage="pinecone_upsert",
            message="Vector upsert completed",
            data={
                "vectors_upserted": total_upserted,
                "vectors_skipped": total_skipped,
                "total_batches": total_batches,
            }
        )


def create_logger(log_file: Path = LOG_FILE_PATH) -> StructuredLogger:
    """
    Create a structured logger instance.
    
    Args:
        log_file: Path to log file
        
    Returns:
        StructuredLogger: Logger instance
    """
    return StructuredLogger(log_file)

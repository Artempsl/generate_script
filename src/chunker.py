"""
Deterministic text chunking module with sentence boundary preservation.

This module implements a deterministic chunking algorithm that:
1. Uses token counting (tiktoken with cl100k_base encoding)
2. Creates chunks with target size and overlap
3. Preserves sentence boundaries when possible
4. Generates sequential, position-based chunk IDs
5. Produces identical output for identical input (deterministic)

Key Design Decisions:
- Token-based chunking ensures consistent sizing for embeddings
- Overlap preserves context continuity across chunk boundaries
- Sentence preservation maintains semantic coherence
- Sequential IDs maintain document order for single-source ingestion
"""

import re
import sys
from typing import List, Dict, Any

try:
    import tiktoken
except ImportError:
    print("❌ ERROR: tiktoken not installed. Run: pip install tiktoken", file=sys.stderr)
    sys.exit(1)

from config import (
    CHUNK_TARGET_TOKENS,
    CHUNK_OVERLAP_TOKENS,
    CHUNK_MAX_TOKENS,
    TOKENIZER_ENCODING,
)


class TextChunk:
    """Represents a single text chunk with metadata."""
    
    def __init__(self, chunk_id: str, text: str, token_count: int, start_char: int, end_char: int):
        """
        Initialize a text chunk.
        
        Args:
            chunk_id: Unique identifier for this chunk
            text: The chunk text content
            token_count: Number of tokens in this chunk
            start_char: Starting character position in original text
            end_char: Ending character position in original text
        """
        self.chunk_id = chunk_id
        self.text = text
        self.token_count = token_count
        self.start_char = start_char
        self.end_char = end_char
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert chunk to dictionary representation."""
        return {
            "chunk_id": self.chunk_id,
            "text": self.text,
            "token_count": self.token_count,
            "start_char": self.start_char,
            "end_char": self.end_char,
            "text_length": len(self.text),
        }
    
    def __repr__(self) -> str:
        preview = self.text[:50].replace("\n", " ")
        return f"TextChunk(id={self.chunk_id}, tokens={self.token_count}, preview='{preview}...')"


def split_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences using a deterministic regex pattern.
    
    This function preserves the exact character positions and is deterministic.
    
    Args:
        text: Text to split into sentences
        
    Returns:
        List[str]: List of sentences
    """
    # Sentence boundary pattern:
    # - Matches period, exclamation, or question mark
    # - Followed by whitespace or end of string
    # - Not preceded by common abbreviations (Mr., Dr., etc.)
    
    # First, protect common abbreviations by temporarily replacing periods
    protected_text = text
    abbreviations = [
        r'\bMr\.', r'\bMrs\.', r'\bMs\.', r'\bDr\.', r'\bProf\.',
        r'\bSr\.', r'\bJr\.', r'\bvs\.', r'\be\.g\.', r'\bi\.e\.',
        r'\bInc\.', r'\bCorp\.', r'\bLtd\.',
    ]
    
    # Use a placeholder that won't appear in normal text
    placeholder = "<!PERIOD!>"
    for abbr in abbreviations:
        protected_text = re.sub(abbr, lambda m: m.group().replace('.', placeholder), protected_text)
    
    # Split on sentence boundaries
    # Pattern: period/exclamation/question followed by space or newline or end
    sentence_pattern = r'([.!?]+)(?:\s+|\n+|$)'
    
    # Split and keep the punctuation
    parts = re.split(sentence_pattern, protected_text)
    
    # Reconstruct sentences (combine text with following punctuation)
    sentences = []
    i = 0
    while i < len(parts):
        if i + 1 < len(parts) and re.match(r'[.!?]+', parts[i + 1]):
            # Combine text with its punctuation
            sentence = parts[i] + parts[i + 1]
            sentences.append(sentence)
            i += 2
        elif parts[i].strip():  # Last part without punctuation
            sentences.append(parts[i])
            i += 1
        else:
            i += 1
    
    # Restore periods in abbreviations
    sentences = [s.replace(placeholder, '.') for s in sentences]
    
    # Remove empty sentences
    sentences = [s for s in sentences if s.strip()]
    
    return sentences


def count_tokens(text: str, encoding_name: str = TOKENIZER_ENCODING) -> int:
    """
    Count the number of tokens in text using tiktoken.
    
    Args:
        text: Text to count tokens for
        encoding_name: Name of the tokenizer encoding to use
        
    Returns:
        int: Number of tokens
    """
    encoding = tiktoken.get_encoding(encoding_name)
    return len(encoding.encode(text))


def create_chunks_with_overlap(
    text: str,
    target_tokens: int = CHUNK_TARGET_TOKENS,
    overlap_tokens: int = CHUNK_OVERLAP_TOKENS,
    max_tokens: int = CHUNK_MAX_TOKENS,
) -> List[TextChunk]:
    """
    Create text chunks with token-based sizing and overlap.
    
    This is the main chunking function. It creates chunks that:
    - Target a specific token count
    - Have overlapping tokens for context continuity
    - Preserve sentence boundaries when possible
    - Are deterministic (same input → same output)
    
    Algorithm:
    1. Split text into sentences
    2. Build chunks by adding sentences until target is reached
    3. When starting a new chunk, go back overlap_tokens to create overlap
    4. Continue until all text is chunked
    
    Args:
        text: Text to chunk
        target_tokens: Target number of tokens per chunk
        overlap_tokens: Number of tokens to overlap between chunks
        max_tokens: Maximum allowed tokens per chunk
        
    Returns:
        List[TextChunk]: List of text chunks with metadata
    """
    if not text or not text.strip():
        return []
    
    # Split into sentences
    sentences = split_into_sentences(text)
    
    if not sentences:
        # Fallback: treat entire text as one sentence
        sentences = [text]
    
    chunks = []
    current_chunk_sentences = []
    current_chunk_tokens = 0
    chunk_counter = 0
    char_position = 0
    
    # Track sentences for overlap
    all_processed_sentences = []
    
    for i, sentence in enumerate(sentences):
        sentence_tokens = count_tokens(sentence)
        
        # Check if adding this sentence would exceed max_tokens
        if current_chunk_tokens + sentence_tokens > max_tokens and current_chunk_sentences:
            # Finalize current chunk
            chunk_text = "".join(current_chunk_sentences)
            chunk_id = f"chunk_{chunk_counter}"
            
            chunk = TextChunk(
                chunk_id=chunk_id,
                text=chunk_text,
                token_count=current_chunk_tokens,
                start_char=char_position,
                end_char=char_position + len(chunk_text),
            )
            chunks.append(chunk)
            
            # Store sentences for potential overlap
            all_processed_sentences.extend(current_chunk_sentences)
            
            # Move character position forward
            char_position += len(chunk_text)
            
            # Prepare next chunk with overlap
            # Go back through processed sentences to create overlap
            overlap_sentences = []
            overlap_token_count = 0
            
            # Go backwards through recent sentences to build overlap
            for prev_sentence in reversed(current_chunk_sentences):
                prev_tokens = count_tokens(prev_sentence)
                if overlap_token_count + prev_tokens <= overlap_tokens:
                    overlap_sentences.insert(0, prev_sentence)
                    overlap_token_count += prev_tokens
                else:
                    break
            
            # Start new chunk with overlap
            current_chunk_sentences = overlap_sentences
            current_chunk_tokens = overlap_token_count
            chunk_counter += 1
        
        # Add current sentence to chunk
        current_chunk_sentences.append(sentence)
        current_chunk_tokens += sentence_tokens
        
        # If we've reached target, consider finalizing (but allow some overflow for sentence completeness)
        if current_chunk_tokens >= target_tokens and i < len(sentences) - 1:
            # Check if next sentence would push us over max_tokens
            next_sentence_tokens = count_tokens(sentences[i + 1]) if i + 1 < len(sentences) else 0
            
            if current_chunk_tokens + next_sentence_tokens > max_tokens:
                # Finalize chunk now
                chunk_text = "".join(current_chunk_sentences)
                chunk_id = f"chunk_{chunk_counter}"
                
                chunk = TextChunk(
                    chunk_id=chunk_id,
                    text=chunk_text,
                    token_count=current_chunk_tokens,
                    start_char=char_position,
                    end_char=char_position + len(chunk_text),
                )
                chunks.append(chunk)
                
                # Store sentences for potential overlap
                all_processed_sentences.extend(current_chunk_sentences)
                
                # Move character position
                char_position += len(chunk_text)
                
                # Prepare overlap for next chunk
                overlap_sentences = []
                overlap_token_count = 0
                
                for prev_sentence in reversed(current_chunk_sentences):
                    prev_tokens = count_tokens(prev_sentence)
                    if overlap_token_count + prev_tokens <= overlap_tokens:
                        overlap_sentences.insert(0, prev_sentence)
                        overlap_token_count += prev_tokens
                    else:
                        break
                
                current_chunk_sentences = overlap_sentences
                current_chunk_tokens = overlap_token_count
                chunk_counter += 1
    
    # Add final chunk if there's remaining text
    if current_chunk_sentences:
        chunk_text = "".join(current_chunk_sentences)
        chunk_id = f"chunk_{chunk_counter}"
        
        chunk = TextChunk(
            chunk_id=chunk_id,
            text=chunk_text,
            token_count=current_chunk_tokens,
            start_char=char_position,
            end_char=char_position + len(chunk_text),
        )
        chunks.append(chunk)
    
    return chunks


def chunk_text(text: str) -> List[TextChunk]:
    """
    Main entry point for text chunking.
    
    This function uses the configuration defaults from config.py.
    
    Args:
        text: Text to chunk
        
    Returns:
        List[TextChunk]: List of text chunks
    """
    return create_chunks_with_overlap(text)


def get_chunks_summary(chunks: List[TextChunk]) -> Dict[str, Any]:
    """
    Get summary statistics about chunks.
    
    Args:
        chunks: List of text chunks
        
    Returns:
        Dict[str, Any]: Summary statistics
    """
    if not chunks:
        return {
            "total_chunks": 0,
            "total_tokens": 0,
            "avg_tokens_per_chunk": 0,
            "min_tokens": 0,
            "max_tokens": 0,
        }
    
    token_counts = [chunk.token_count for chunk in chunks]
    
    return {
        "total_chunks": len(chunks),
        "total_tokens": sum(token_counts),
        "avg_tokens_per_chunk": sum(token_counts) / len(token_counts),
        "min_tokens": min(token_counts),
        "max_tokens": max(token_counts),
    }


# =============================================================================
# CLI FOR TESTING
# =============================================================================

if __name__ == "__main__":
    """Test chunker from command line."""
    from pdf_extractor import extract_and_validate_pdf
    from config import PDF_FILE_PATH
    
    print("=" * 80)
    print("DETERMINISTIC CHUNKING TEST")
    print("=" * 80)
    
    # Extract text from PDF
    print(f"\n1. Extracting text from: {PDF_FILE_PATH}")
    text = extract_and_validate_pdf(PDF_FILE_PATH)
    print(f"   ✓ Extracted {len(text.split())} words")
    
    # Chunk text (first run)
    print(f"\n2. Chunking text (Run 1)...")
    chunks_run1 = chunk_text(text)
    summary1 = get_chunks_summary(chunks_run1)
    
    print(f"   ✓ Created {summary1['total_chunks']} chunks")
    print(f"   - Total tokens: {summary1['total_tokens']}")
    print(f"   - Avg tokens/chunk: {summary1['avg_tokens_per_chunk']:.1f}")
    print(f"   - Min tokens: {summary1['min_tokens']}")
    print(f"   - Max tokens: {summary1['max_tokens']}")
    
    # Chunk text again (second run) to test determinism
    print(f"\n3. Chunking text (Run 2) to verify determinism...")
    chunks_run2 = chunk_text(text)
    summary2 = get_chunks_summary(chunks_run2)
    
    # Compare runs
    if summary1 == summary2:
        print("   ✓ Chunk summaries match!")
    else:
        print("   ❌ Chunk summaries differ!")
        sys.exit(1)
    
    # Verify chunk IDs and token counts match
    ids_match = all(c1.chunk_id == c2.chunk_id for c1, c2 in zip(chunks_run1, chunks_run2))
    tokens_match = all(c1.token_count == c2.token_count for c1, c2 in zip(chunks_run1, chunks_run2))
    text_match = all(c1.text == c2.text for c1, c2 in zip(chunks_run1, chunks_run2))
    
    if ids_match and tokens_match and text_match:
        print("   ✓ All chunks identical (deterministic)!")
    else:
        print("   ❌ Chunks differ between runs!")
        sys.exit(1)
    
    # Show first few chunks as examples
    print(f"\n4. Sample chunks:")
    print("-" * 80)
    for i, chunk in enumerate(chunks_run1[:3]):
        preview = chunk.text[:150].replace("\n", " ")
        print(f"\n   {chunk.chunk_id}:")
        print(f"   - Tokens: {chunk.token_count}")
        print(f"   - Text length: {len(chunk.text)} chars")
        print(f"   - Preview: {preview}...")
    
    print("\n" + "=" * 80)
    print("✓ CHUNKING TEST PASSED - Fully deterministic!")
    print("=" * 80)

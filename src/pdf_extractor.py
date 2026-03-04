"""
PDF text extraction module.

This module provides functionality to extract text content from PDF files
with proper error handling and validation.

Key features:
- Extracts text from all pages
- Preserves newlines and structure
- Validates extraction quality
- Handles encrypted/corrupted PDFs gracefully
"""

import sys
from pathlib import Path
from typing import Tuple

try:
    from pypdf import PdfReader
except ImportError:
    print("❌ ERROR: pypdf not installed. Run: pip install pypdf", file=sys.stderr)
    sys.exit(1)


class PDFExtractionError(Exception):
    """Custom exception for PDF extraction errors."""
    pass


def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Extract all text content from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        str: Extracted text content
        
    Raises:
        PDFExtractionError: If PDF cannot be read or is invalid
    """
    if not pdf_path.exists():
        raise PDFExtractionError(f"PDF file not found: {pdf_path}")
    
    if not pdf_path.is_file():
        raise PDFExtractionError(f"Path is not a file: {pdf_path}")
    
    try:
        reader = PdfReader(pdf_path)
        
        # Check if PDF is encrypted
        if reader.is_encrypted:
            raise PDFExtractionError("PDF is encrypted and cannot be read")
        
        # Extract text from all pages
        text_parts = []
        for page_num, page in enumerate(reader.pages, start=1):
            try:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            except Exception as e:
                # Log page extraction failure but continue
                print(f"⚠ Warning: Failed to extract page {page_num}: {e}", file=sys.stderr)
        
        if not text_parts:
            raise PDFExtractionError("No text could be extracted from PDF")
        
        # Join all pages with newlines
        full_text = "\n\n".join(text_parts)
        
        return full_text
    
    except PDFExtractionError:
        raise
    except Exception as e:
        raise PDFExtractionError(f"Failed to read PDF: {e}")


def validate_extracted_text(text: str, min_words: int = 100) -> Tuple[bool, str]:
    """
    Validate that extracted text meets quality requirements.
    
    Args:
        text: Extracted text to validate
        min_words: Minimum number of words required
        
    Returns:
        Tuple[bool, str]: (is_valid, message)
    """
    if not text or not text.strip():
        return False, "Extracted text is empty"
    
    # Count words (simple split on whitespace)
    word_count = len(text.split())
    
    if word_count < min_words:
        return False, f"Extracted text too short: {word_count} words (minimum: {min_words})"
    
    # Check for reasonable character variety (not just repeated characters)
    unique_chars = len(set(text.replace(" ", "").replace("\n", "")))
    if unique_chars < 10:
        return False, "Extracted text has insufficient character variety"
    
    return True, f"Validation passed: {word_count} words extracted"


def get_text_preview(text: str, length: int = 500) -> str:
    """
    Get a preview of the extracted text.
    
    Args:
        text: Full text
        length: Number of characters to include in preview
        
    Returns:
        str: Text preview
    """
    preview = text[:length].replace("\n", " ").strip()
    if len(text) > length:
        preview += "..."
    return preview


def extract_and_validate_pdf(pdf_path: Path, min_words: int = 100) -> str:
    """
    Extract text from PDF and validate quality.
    
    This is the main entry point for PDF extraction.
    
    Args:
        pdf_path: Path to PDF file
        min_words: Minimum number of words required
        
    Returns:
        str: Validated extracted text
        
    Raises:
        PDFExtractionError: If extraction fails or validation fails
    """
    # Extract text
    text = extract_text_from_pdf(pdf_path)
    
    # Validate
    is_valid, message = validate_extracted_text(text, min_words)
    if not is_valid:
        raise PDFExtractionError(f"Validation failed: {message}")
    
    return text


# =============================================================================
# CLI FOR TESTING
# =============================================================================

if __name__ == "__main__":
    """Test PDF extraction from command line."""
    import sys
    from config import PDF_FILE_PATH
    
    print(f"Extracting text from: {PDF_FILE_PATH}")
    print("-" * 80)
    
    try:
        text = extract_and_validate_pdf(PDF_FILE_PATH)
        
        word_count = len(text.split())
        char_count = len(text)
        line_count = text.count("\n") + 1
        
        print(f"✓ Extraction successful!")
        print(f"  - Characters: {char_count:,}")
        print(f"  - Words: {word_count:,}")
        print(f"  - Lines: {line_count:,}")
        print()
        print("Text preview (first 500 characters):")
        print("-" * 80)
        print(get_text_preview(text, 500))
        print("-" * 80)
        
    except PDFExtractionError as e:
        print(f"❌ ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}", file=sys.stderr)
        sys.exit(1)

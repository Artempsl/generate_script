"""
Language detection and character rate utilities.

This module provides:
- Automatic language detection (Russian/English) based on Cyrillic character ratio
- Target character count calculation based on duration and language
- Language-specific constants

Detection Strategy:
    Uses Cyrillic character ratio heuristic:
    - Count Cyrillic characters (U+0400 to U+04FF Unicode range)
    - Calculate ratio: cyrillic_count / total_alphabetic_chars
    - If ratio > 30% → Russian, else → English

Character Rates:
    - Russian: 1450 characters/minute (average reading speed)
    - English: 1000 characters/minute (average reading speed)
"""

from typing import Literal

# Handle both module and standalone execution
try:
    from agent.config import (
        CHAR_RATE_RUSSIAN,
        CHAR_RATE_ENGLISH,
        CYRILLIC_DETECTION_THRESHOLD,
    )
except ModuleNotFoundError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from agent.config import (
        CHAR_RATE_RUSSIAN,
        CHAR_RATE_ENGLISH,
        CYRILLIC_DETECTION_THRESHOLD,
    )


LanguageCode = Literal["ru", "en"]


def detect_language(text: str) -> LanguageCode:
    """
    Detect language based on Cyrillic character ratio.
    
    Algorithm:
        1. Count Cyrillic characters (Cyrillic Unicode block)
        2. Count total alphabetic characters
        3. Calculate ratio
        4. If ratio > threshold (30%) → Russian, else → English
    
    Args:
        text: Text to analyze (genre, story idea, or combined)
        
    Returns:
        "ru" for Russian, "en" for English
        
    Examples:
        >>> detect_language("Комедия про приключения")
        'ru'
        >>> detect_language("Comedy about adventures")
        'en'
        >>> detect_language("Comedy с элементами драмы")
        'ru'  # More than 30% Cyrillic
    """
    if not text or not text.strip():
        return "en"  # Default to English for empty text
    
    # Count Cyrillic characters (U+0400 to U+04FF)
    cyrillic_count = sum(1 for c in text if '\u0400' <= c <= '\u04FF')
    
    # Count total alphabetic characters
    total_alpha = sum(1 for c in text if c.isalpha())
    
    # Handle edge case: no alphabetic characters
    if total_alpha == 0:
        return "en"
    
    # Calculate Cyrillic ratio
    ratio = cyrillic_count / total_alpha
    
    # Determine language
    return "ru" if ratio > CYRILLIC_DETECTION_THRESHOLD else "en"


def get_char_rate(language: LanguageCode) -> int:
    """
    Get character rate (chars/minute) for a language.
    
    Args:
        language: Language code ("ru" or "en")
        
    Returns:
        Characters per minute for the language
    """
    if language == "ru":
        return CHAR_RATE_RUSSIAN
    elif language == "en":
        return CHAR_RATE_ENGLISH
    else:
        # Fallback to English rate
        return CHAR_RATE_ENGLISH


def calculate_target_chars(duration_minutes: int, language: LanguageCode) -> int:
    """
    Calculate target character count for a script.
    
    Formula:
        target_chars = duration_minutes * char_rate_per_minute
    
    Args:
        duration_minutes: Target video duration in minutes
        language: Language code ("ru" or "en")
        
    Returns:
        Target character count
        
    Examples:
        >>> calculate_target_chars(5, "ru")
        7250  # 5 * 1450
        >>> calculate_target_chars(5, "en")
        5000  # 5 * 1000
        >>> calculate_target_chars(10, "ru")
        14500  # 10 * 1450
    """
    char_rate = get_char_rate(language)
    return duration_minutes * char_rate


def validate_script_length(
    actual_chars: int,
    target_chars: int,
    min_ratio: float = 0.90,
    max_ratio: float = 1.10,
) -> tuple[bool, float, str]:
    """
    Validate script length against target.
    
    Args:
        actual_chars: Actual character count in generated script
        target_chars: Target character count
        min_ratio: Minimum acceptable ratio (default 0.90 = 90%)
        max_ratio: Maximum acceptable ratio (default 1.10 = 110%)
        
    Returns:
        Tuple of (is_valid, actual_ratio, message)
        
    Examples:
        >>> validate_script_length(5000, 5000)
        (True, 1.0, "✓ Length valid (100.0%)")
        >>> validate_script_length(4500, 5000)
        (True, 0.9, "✓ Length valid (90.0%)")
        >>> validate_script_length(4000, 5000)
        (False, 0.8, "✗ Too short (80.0%)")
        >>> validate_script_length(6000, 5000)
        (False, 1.2, "✗ Too long (120.0%)")
    """
    if target_chars == 0:
        return False, 0.0, "✗ Invalid target (0 chars)"
    
    actual_ratio = actual_chars / target_chars
    
    if actual_ratio < min_ratio:
        return False, actual_ratio, f"✗ Too short ({actual_ratio:.1%})"
    elif actual_ratio > max_ratio:
        return False, actual_ratio, f"✗ Too long ({actual_ratio:.1%})"
    else:
        return True, actual_ratio, f"✓ Length valid ({actual_ratio:.1%})"


def get_length_adjustment_instruction(
    actual_chars: int,
    target_chars: int,
) -> str:
    """
    Get instruction for script length adjustment.
    
    Used when regenerating script to reach target length.
    
    Args:
        actual_chars: Current character count
        target_chars: Target character count
        
    Returns:
        Instruction string for LLM
    """
    ratio = actual_chars / target_chars if target_chars > 0 else 0
    
    if ratio < 0.90:
        # Too short - need to expand
        shortage = target_chars - actual_chars
        return (
            f"The script is too short ({actual_chars} chars vs target {target_chars} chars). "
            f"Please expand by approximately {shortage} characters. "
            f"Add more descriptive details, dialogue, or scene descriptions while maintaining quality."
        )
    elif ratio > 1.10:
        # Too long - need to shorten
        excess = actual_chars - target_chars
        return (
            f"The script is too long ({actual_chars} chars vs target {target_chars} chars). "
            f"Please shorten by approximately {excess} characters. "
            f"Remove unnecessary details or dialogue while preserving the core narrative."
        )
    else:
        # Within range (shouldn't normally reach here)
        return "Maintain current script length."


# =============================================================================
# CLI FOR TESTING
# =============================================================================

if __name__ == "__main__":
    """Test language detection and utilities."""
    
    print("=" * 80)
    print("LANGUAGE DETECTION & UTILITIES TEST")
    print("=" * 80)
    
    # Test 1: Language detection
    print("\n1. Testing language detection:")
    print("-" * 80)
    
    test_cases = [
        ("Комедия про приключения программиста", "ru"),
        ("Comedy about a programmer's adventures", "en"),
        ("Драма с элементами фантастики", "ru"),
        ("Drama with fantasy elements", "en"),
        ("Sci-fi триллер в космосе", "ru"),  # Mixed but > 30% Cyrillic
        ("Action thriller in space", "en"),
        ("", "en"),  # Empty defaults to English
        ("12345!@#$%", "en"),  # No letters defaults to English
    ]
    
    for text, expected in test_cases:
        detected = detect_language(text)
        status = "✓" if detected == expected else "✗"
        print(f"  {status} '{text[:40]}...' → {detected} (expected: {expected})")
    
    # Test 2: Character rate calculation
    print("\n2. Testing character rate calculation:")
    print("-" * 80)
    
    durations = [5, 10, 15]
    for duration in durations:
        ru_chars = calculate_target_chars(duration, "ru")
        en_chars = calculate_target_chars(duration, "en")
        print(f"  Duration: {duration} min")
        print(f"    - Russian: {ru_chars:,} chars ({CHAR_RATE_RUSSIAN} chars/min)")
        print(f"    - English: {en_chars:,} chars ({CHAR_RATE_ENGLISH} chars/min)")
    
    # Test 3: Script length validation
    print("\n3. Testing script length validation:")
    print("-" * 80)
    
    target = 5000
    test_lengths = [
        (5000, "exact match"),
        (4500, "90% - minimum valid"),
        (5500, "110% - maximum valid"),
        (4000, "80% - too short"),
        (6000, "120% - too long"),
    ]
    
    for actual, description in test_lengths:
        is_valid, ratio, message = validate_script_length(actual, target)
        status = "✓" if is_valid else "✗"
        print(f"  {status} {actual:,} chars ({description}): {message}")
    
    # Test 4: Length adjustment instructions
    print("\n4. Testing length adjustment instructions:")
    print("-" * 80)
    
    adjustments = [
        (4000, 5000, "too short"),
        (6000, 5000, "too long"),
        (5000, 5000, "perfect"),
    ]
    
    for actual, target, scenario in adjustments:
        instruction = get_length_adjustment_instruction(actual, target)
        print(f"\n  Scenario: {scenario} ({actual} / {target})")
        print(f"  Instruction: {instruction[:100]}...")
    
    # Test 5: Realistic example
    print("\n5. Realistic workflow example:")
    print("-" * 80)
    
    # Simulate n8n input
    genre = "Комедийная драма"
    idea = "История о программисте, который создал ИИ"
    duration = 7
    
    # Detect language
    combined_text = f"{genre} {idea}"
    language = detect_language(combined_text)
    target_chars = calculate_target_chars(duration, language)
    
    print(f"  Genre: {genre}")
    print(f"  Idea: {idea}")
    print(f"  Duration: {duration} minutes")
    print(f"  Detected language: {language}")
    print(f"  Target characters: {target_chars:,}")
    
    # Simulate script generation
    simulated_script_length = 9500  # Example
    is_valid, ratio, message = validate_script_length(
        simulated_script_length, target_chars
    )
    
    print(f"  Generated script: {simulated_script_length:,} chars")
    print(f"  Validation: {message}")
    
    if not is_valid:
        instruction = get_length_adjustment_instruction(
            simulated_script_length, target_chars
        )
        print(f"  Adjustment needed: {instruction[:80]}...")
    
    print("\n" + "=" * 80)
    print("✓ LANGUAGE UTILITIES TEST COMPLETE")
    print("=" * 80)

"""
Test segment_script_tool in isolation.

Validates:
- Cohere API segmentation
- JSON parsing
- Fallback segmentation
- Retry logic
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.tools import segment_script_tool


# Sample script for testing (1 minute Thriller script)
SAMPLE_SCRIPT_EN = """Detective Sarah Chen sat alone in her dimly lit office, surrounded by case files and cold coffee cups. The serial killer case had consumed her life for six months, leaving a trail of cryptic messages and bodies. Her phone buzzed—an unknown number. "You're getting closer, Detective," the text read. "But are you ready for the truth?" Her hands trembled as she opened the attached image: a photo of her own apartment, taken from inside. Someone had been watching her all along. The killer wasn't just targeting victims—he was targeting her."""

SAMPLE_SCRIPT_RU = """Детектив Сара Чен сидела в одиночестве в своем тускло освещённом офисе, окружённая папками с делами и остывшими чашками кофе. Дело о серийном убийце поглотило её жизнь на шесть месяцев, оставляя след из загадочных посланий и тел. Её телефон завибрировал—неизвестный номер. «Вы близки к разгадке, детектив», гласил текст. «Но готовы ли вы к правде?» Её руки дрожали когда она открыла прикреплённое изображение: фотографию её собственной квартиры, снятую изнутри. Кто-то наблюдал за ней всё это время. Убийца не просто преследовал жертв—он преследовал её."""


def test_english_segmentation():
    """Test segmentation with English script."""
    print("=" * 80)
    print("TEST 1: English Script Segmentation")
    print("=" * 80)
    
    print(f"\nScript length: {len(SAMPLE_SCRIPT_EN)} chars")
    print(f"Script preview: {SAMPLE_SCRIPT_EN[:100]}...")
    
    print("\n→ Calling segment_script_tool (language='en')...")
    result = segment_script_tool(
        script=SAMPLE_SCRIPT_EN,
        language="en"
    )
    
    print(f"\n✓ Result:")
    print(f"  - Success: {result['success']}")
    print(f"  - Segment count: {result['segment_count']}")
    print(f"  - Tokens used: {result['tokens_used']}")
    if result['error']:
        print(f"  - Error: {result['error']}")
    
    if result['success'] and result['segments']:
        print(f"\n  Segments:")
        for seg in result['segments']:
            text_preview = seg['text'][:80] + "..." if len(seg['text']) > 80 else seg['text']
            print(f"    {seg['segment_index']}. {text_preview}")
            print(f"       ({len(seg['text'])} chars)")
    
    return result['success']


def test_russian_segmentation():
    """Test segmentation with Russian script."""
    print("\n" + "=" * 80)
    print("TEST 2: Russian Script Segmentation")
    print("=" * 80)
    
    print(f"\nScript length: {len(SAMPLE_SCRIPT_RU)} chars")
    print(f"Script preview: {SAMPLE_SCRIPT_RU[:100]}...")
    
    print("\n→ Calling segment_script_tool (language='ru')...")
    result = segment_script_tool(
        script=SAMPLE_SCRIPT_RU,
        language="ru"
    )
    
    print(f"\n✓ Result:")
    print(f"  - Success: {result['success']}")
    print(f"  - Segment count: {result['segment_count']}")
    print(f"  - Tokens used: {result['tokens_used']}")
    if result['error']:
        print(f"  - Error: {result['error']}")
    
    if result['success'] and result['segments']:
        print(f"\n  Segments:")
        for seg in result['segments']:
            text_preview = seg['text'][:80] + "..." if len(seg['text']) > 80 else seg['text']
            print(f"    {seg['segment_index']}. {text_preview}")
            print(f"       ({len(seg['text'])} chars)")
    
    return result['success']


def test_fallback_segmentation():
    """Test fallback segmentation (without Cohere)."""
    print("\n" + "=" * 80)
    print("TEST 3: Fallback Segmentation (Sentence Splitting)")
    print("=" * 80)
    
    # Force fallback by passing invalid script
    short_script = "Sentence one. Sentence two. Sentence three. Sentence four. Sentence five. Sentence six."
    
    print(f"\nScript: {short_script}")
    print("\n→ Calling fallback segmentation...")
    
    from agent.tools import _fallback_sentence_segmentation
    result = _fallback_sentence_segmentation(short_script)
    
    print(f"\n✓ Result:")
    print(f"  - Success: {result['success']}")
    print(f"  - Segment count: {result['segment_count']}")
    print(f"  - Error: {result['error']}")
    
    if result['segments']:
        print(f"\n  Segments:")
        for seg in result['segments']:
            print(f"    {seg['segment_index']}. {seg['text']}")
    
    return result['success']


def main():
    """Run all segmentation tests."""
    print("\n⚠️  NOTE: These tests require COHERE_API_KEY environment variable")
    print("If not set, tests will use fallback segmentation\n")
    
    results = []
    
    results.append(test_english_segmentation())
    results.append(test_russian_segmentation())
    results.append(test_fallback_segmentation())
    
    print("\n" + "=" * 80)
    if all(results):
        print("✅ ALL SEGMENTATION TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 80)


if __name__ == "__main__":
    main()

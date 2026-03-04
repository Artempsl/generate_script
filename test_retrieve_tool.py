"""Test retrieve_tool directly."""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from agent.tools import retrieve_tool

# Test query
query = "Comedy storytelling techniques"
language = "en"

print("=" * 70)
print(f"Testing retrieve_tool")
print(f"Query: {query}")
print(f"Language: {language}")
print("=" * 70)

result = retrieve_tool(query=query, language=language, top_k=3)

print(f"\nSuccess: {result['success']}")
print(f"Sources count: {result['sources_count']}")
print(f"Tokens used: {result['tokens_used']}")
print(f"Error: {result.get('error', 'None')}")

if result['context']:
    print(f"\nContext length: {len(result['context'])} chars")
    print(f"Context preview (first 500 chars):")
    print("-" * 70)
    print(result['context'][:500])
    print("...")
else:
    print("\n⚠ No context retrieved!")

print("\n" + "=" * 70)

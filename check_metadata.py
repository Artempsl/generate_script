"""Check vector metadata in Pinecone."""
import os
from pinecone import Pinecone
import cohere

# Initialize
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
co = cohere.ClientV2(api_key=os.getenv("COHERE_API_KEY"))
index = pc.Index("storytelling")

# Create query embedding
test_query = "Comedy storytelling techniques"
embed_response = co.embed(
    texts=[test_query],
    model="embed-english-v3.0",
    input_type="search_query",
    embedding_types=["float"]
)
query_embedding = embed_response.embeddings.float_[0]

# Query Pinecone
results = index.query(
    vector=query_embedding,
    top_k=3,
    include_metadata=True
)

print("=" * 70)
print(f"QUERY: '{test_query}'")
print(f"MATCHES FOUND: {len(results.matches)}")
print("=" * 70)

for i, match in enumerate(results.matches, 1):
    print(f"\n{'='*70}")
    print(f"MATCH {i}:")
    print(f"  ID: {match.id}")
    print(f"  Score: {match.score:.4f}")
    print(f"  Metadata keys: {list(match.metadata.keys())}")
    print(f"  Metadata:")
    for key, value in match.metadata.items():
        if isinstance(value, str) and len(value) > 100:
            print(f"    {key}: {value[:100]}...")
        else:
            print(f"    {key}: {value}")
    
    # Check text field specifically
    text_value = match.metadata.get("text", "")
    print(f"\n  HAS 'text' field: {bool(text_value)}")
    if text_value:
        print(f"  Text length: {len(text_value)} chars")
    else:
        print(f"  ⚠ WARNING: 'text' field is EMPTY or missing!")

print("\n" + "=" * 70)

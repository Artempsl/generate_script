"""Check Pinecone index status."""
import os
from pinecone import Pinecone

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("storytelling")

# Get stats
stats = index.describe_index_stats()

print("=" * 60)
print("PINECONE INDEX STATUS")
print("=" * 60)
print(f"Index name: storytelling")
print(f"Total vectors: {stats.total_vector_count}")
print(f"Dimension: {stats.dimension}")
print(f"\nNamespaces: {stats.namespaces}")
print("=" * 60)

# Try a sample query
if stats.total_vector_count > 0:
    print("\nTesting sample query...")
    import cohere
    
    co = cohere.ClientV2(api_key=os.getenv("COHERE_API_KEY"))
    
    # Create query embedding
    test_query = "comedy storytelling techniques"
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
    
    print(f"Query: '{test_query}'")
    print(f"Matches found: {len(results.matches)}")
    
    for i, match in enumerate(results.matches, 1):
        print(f"\nMatch {i}:")
        print(f"  Score: {match.score:.4f}")
        print(f"  ID: {match.id}")
        if 'text' in match.metadata:
            preview = match.metadata['text'][:150]
            print(f"  Text preview: {preview}...")
else:
    print("\n⚠ Index is EMPTY!")

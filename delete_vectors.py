"""Delete all vectors from Pinecone index."""
import os
from pinecone import Pinecone

# Initialize
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("storytelling")

# Get stats before
stats_before = index.describe_index_stats()
print(f"Vectors before deletion: {stats_before.total_vector_count}")

# Delete all vectors in default namespace
print("Deleting all vectors...")
index.delete(delete_all=True, namespace="")

print("✓ All vectors deleted")

# Confirm deletion
import time
time.sleep(2)  # Wait for propagation
stats_after = index.describe_index_stats()
print(f"Vectors after deletion: {stats_after.total_vector_count}")

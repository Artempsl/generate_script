# Quick test to check if Python sees environment variables
import os

print("Python Environment Variable Check:")
print(f"  OPENAI_API_KEY: {'SET (' + str(len(os.environ.get('OPENAI_API_KEY', ''))) + ' chars)' if os.environ.get('OPENAI_API_KEY') else 'NOT SET'}")
print(f"  PINECONE_API_KEY: {'SET (' + str(len(os.environ.get('PINECONE_API_KEY', ''))) + ' chars)' if os.environ.get('PINECONE_API_KEY') else 'NOT SET'}")
print(f"  COHERE_API_KEY: {'SET (' + str(len(os.environ.get('COHERE_API_KEY', ''))) + ' chars)' if os.environ.get('COHERE_API_KEY') else 'NOT SET'}")
print(f"  SERPAPI_API_KEY: {'SET (' + str(len(os.environ.get('SERPAPI_API_KEY', ''))) + ' chars)' if os.environ.get('SERPAPI_API_KEY') else 'NOT SET'}")

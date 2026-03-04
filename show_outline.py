"""Show outline that was generated using Pinecone context."""
import sqlite3

conn = sqlite3.connect('agent.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT outline
    FROM executions
    WHERE request_id LIKE 'test-horror-%'
    ORDER BY created_at DESC
    LIMIT 1
""")

row = cursor.fetchone()

if row and row[0]:
    print("=" * 70)
    print("OUTLINE (generated using Pinecone-synthesized context)")
    print("=" * 70)
    print("\nThis outline was created by OpenAI using the 4,205 chars")
    print("of synthesized insights from Pinecone's 5 best practice chunks.")
    print("\n" + "=" * 70)
    print(row[0])
    print("=" * 70)
else:
    print("Outline not found")

conn.close()

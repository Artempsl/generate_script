"""Direct database query for noir test."""
import sqlite3

conn = sqlite3.connect("agent.db")
cursor = conn.cursor()

# Check for noir test
cursor.execute("""
    SELECT request_id, status, char_count, iteration_count, tokens_used_total, created_at
    FROM executions 
    WHERE request_id LIKE 'test-noir-%'
    ORDER BY created_at DESC 
    LIMIT 1
""")

result = cursor.fetchone()

if result:
    print(f"✓ Noir detective test found!")
    print(f"  Request ID: {result[0]}")
    print(f"  Status: {result[1]}")
    print(f"  Characters: {result[2]}")
    print(f"  Iterations: {result[3]}")
    print(f"  Tokens: {result[4]}")
    print(f"  Created: {result[5]}")
else:
    print("✗ No noir test found in database")
    print("\nAll test executions:")
    cursor.execute("""
        SELECT request_id, status, genre, created_at
        FROM executions
        ORDER BY created_at DESC
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"  {row[0]} | {row[1]} | {row[2]} | {row[3]}")

conn.close()

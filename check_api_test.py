import sqlite3

conn = sqlite3.connect('agent.db')
cursor = conn.cursor()

cursor.execute('''
    SELECT request_id, genre, status, error_message, created_at
    FROM executions 
    WHERE request_id LIKE '%api%' OR genre = 'Action'
    ORDER BY created_at DESC
''')

print("\n=== API Test Results ===\n")
for row in cursor.fetchall():
    req_id, genre, status, error, created = row
    print(f"Request ID: {req_id}")
    print(f"Genre: {genre}")
    print(f"Status: {status}")
    print(f"Time: {created}")
    if error:
        print(f"\nERROR MESSAGE:")
        print("-" * 60)
        print(error)
        print("-" * 60)
    print()

conn.close()

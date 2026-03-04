import sqlite3

conn = sqlite3.connect('agent.db')
cursor = conn.cursor()

print("\n=== Last 5 Tests ===\n")
cursor.execute('''
    SELECT request_id, genre, char_count, status, created_at 
    FROM executions 
    ORDER BY created_at DESC 
    LIMIT 5
''')

for row in cursor.fetchall():
    req_id, genre, chars, status, created = row
    chars_str = f"{chars:5}" if chars is not None else "None "
    print(f"{req_id[:35]:35} | {genre:15} | {chars_str} chars | {status}")

print("\n=== Search for Noir ===\n")
cursor.execute('''
    SELECT request_id, genre, char_count, status 
    FROM executions 
    WHERE genre LIKE '%oir%' OR request_id LIKE '%noir%'
''')

noir_tests = cursor.fetchall()
if noir_tests:
    for row in noir_tests:
        print(f"Found: {row[0]} | {row[1]} | {row[2]} chars | {row[3]}")
else:
    print("❌ No noir detective tests found in database")

conn.close()

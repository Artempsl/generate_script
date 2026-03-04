import sqlite3
from datetime import datetime

conn = sqlite3.connect('agent.db')
cur = conn.cursor()

# Get all requests from last hour
results = cur.execute('''
    SELECT request_id, project_name, genre, duration, 
           char_count, iteration_count, status, created_at
    FROM executions
    ORDER BY created_at DESC
    LIMIT 5
''').fetchall()

print("Recent executions:")
print("=" * 80)
for row in results:
    req_id, proj, genre, dur, chars, iters, status, created = row
    print(f"{created} | {req_id} | {genre} | {dur}min | {chars}chars | {status}")

conn.close()

import sqlite3
from datetime import datetime, timezone, timedelta

conn = sqlite3.connect('agent.db')
cursor = conn.cursor()

# Check for recent errors (last hour)
one_hour_ago = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()

print("\n=== ERROR EXECUTIONS (last hour) ===\n")
cursor.execute('''
    SELECT request_id, genre, status, error_message, created_at
    FROM executions 
    WHERE status = 'error' AND created_at > ?
    ORDER BY created_at DESC
''', (one_hour_ago,))

errors = cursor.fetchall()
if errors:
    for row in errors:
        req_id, genre, status, error, created = row
        print(f"ID: {req_id}")
        print(f"Genre: {genre}")
        print(f"Error: {error}")
        print(f"Time: {created}")
        print("-" * 60)
else:
    print("❌ No error executions found in last hour")

print("\n=== ALL EXECUTIONS (last 2 hours) ===\n")
two_hours_ago = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
cursor.execute('''
    SELECT request_id, genre, status, created_at
    FROM executions 
    WHERE created_at > ?
    ORDER BY created_at DESC
''', (two_hours_ago,))

all_recent = cursor.fetchall()
print(f"Total: {len(all_recent)} executions\n")
for row in all_recent:
    req_id, genre, status, created = row
    time_str = created.split('T')[1][:8] if 'T' in created else created
    print(f"{time_str} | {req_id[:30]:30} | {genre:15} | {status}")

conn.close()

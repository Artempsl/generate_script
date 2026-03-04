"""Fix database records with NULL request_id."""

import sqlite3
from uuid import uuid4

db_path = "agent.db"

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Find records with empty request_id
cursor.execute("SELECT rowid FROM executions WHERE request_id IS NULL OR request_id = ''")
rows = cursor.fetchall()

print(f"Found {len(rows)} records with empty request_id")

# Update each record with a new UUID
for row in rows:
    rowid = row[0]
    new_id = str(uuid4())
    cursor.execute("UPDATE executions SET request_id = ? WHERE rowid = ?", (new_id, rowid))
    print(f"  Updated rowid {rowid} -> {new_id}")

# Commit changes
conn.commit()
conn.close()

print(f"\n✓ Database fixed! Updated {len(rows)} records")

import sqlite3

conn = sqlite3.connect('agent.db')
cur = conn.cursor()

# Check tables
tables = cur.execute('SELECT name FROM sqlite_master WHERE type="table"').fetchall()
print("Tables:", [t[0] for t in tables])

# Try to find script in any of the tables
for table_name in [t[0] for t in tables]:
    try:
        columns = cur.execute(f'PRAGMA table_info({table_name})').fetchall()
        col_names = [c[1] for c in columns]
        
        if 'script' in col_names and 'request_id' in col_names:
            print(f"\nFound 'script' column in table: {table_name}")
            result = cur.execute(f'SELECT script, char_count FROM {table_name} WHERE request_id=?', 
                               ('test-react-1772641331',)).fetchone()
            if result:
                script, char_count = result
                print(f"\nScript ({char_count} chars):")
                print("=" * 80)
                print(script)
                break
    except Exception as e:
        continue

conn.close()

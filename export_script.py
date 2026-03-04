"""Extract latest script from database and save to file."""
import sqlite3
from datetime import datetime

conn = sqlite3.connect('agent.db')
query = """
    SELECT project_name, genre, duration, language, script, 
           char_count, iteration_count, tokens_used_total, created_at
    FROM executions 
    WHERE status='success' 
    ORDER BY created_at DESC 
    LIMIT 1
"""
row = conn.execute(query).fetchone()
conn.close()

if row:
    filename = f'generated_script_{int(datetime.now().timestamp())}.txt'
    
    content = f"""PROJECT: {row[0]}
GENRE: {row[1]}
DURATION: {row[2]} min
LANGUAGE: {row[3]}
LENGTH: {row[5]} characters
ITERATIONS: {row[6]}
TOKENS USED: {row[7]}
GENERATED: {row[8]}

{'=' * 70}

{row[4]}
"""
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f'✅ Script saved to: {filename}')
    print(f'\nPreview (first 300 chars):')
    print('=' * 70)
    print(row[4][:300] + '...')
    print('=' * 70)
else:
    print('❌ No successful executions found in database')

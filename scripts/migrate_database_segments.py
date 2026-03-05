"""
Database migration script: Add segments_json and audio_files_count columns.

This script safely migrates the existing agent.db to support the new
segmentation and audio generation features.

Usage:
    python scripts/migrate_database_segments.py

Changes:
    - Adds segments_json TEXT column
    - Adds audio_files_count INTEGER column
    - Initializes existing records with empty values
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.config import DATABASE_PATH


def migrate_database(auto_confirm: bool = False):
    """Execute database migration."""
    print("=" * 80)
    print("DATABASE MIGRATION: Add Segmentation Support")
    print("=" * 80)
    print(f"Database: {DATABASE_PATH}")
    print()
    
    # Backup reminder
    if not auto_confirm:
        print("⚠️  BACKUP REMINDER:")
        print("   It's recommended to backup agent.db before migration")
        print("   Copy: agent.db → agent.db.backup")
        print()
        
        response = input("Continue with migration? (yes/no): ")
        if response.lower() != "yes":
            print("Migration cancelled.")
            return
        
        print()
    else:
        print("→ Auto-confirm enabled, proceeding with migration...")
        print()
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(executions)")
        columns = [row[1] for row in cursor.fetchall()]
        
        print("Current columns:")
        for col in columns:
            print(f"  - {col}")
        print()
        
        # Add segments_json column
        if "segments_json" not in columns:
            print("→ Adding segments_json column...")
            cursor.execute("ALTER TABLE executions ADD COLUMN segments_json TEXT")
            print("  ✓ segments_json added")
        else:
            print("  ℹ segments_json already exists")
        
        # Add audio_files_count column
        if "audio_files_count" not in columns:
            print("→ Adding audio_files_count column...")
            cursor.execute("ALTER TABLE executions ADD COLUMN audio_files_count INTEGER DEFAULT 0")
            print("  ✓ audio_files_count added")
        else:
            print("  ℹ audio_files_count already exists")
        
        # Initialize existing records with empty values
        print("\n→ Initializing existing records...")
        cursor.execute("""
            UPDATE executions 
            SET segments_json = '[]', 
                audio_files_count = 0 
            WHERE segments_json IS NULL OR audio_files_count IS NULL
        """)
        rows_updated = cursor.rowcount
        print(f"  ✓ Updated {rows_updated} existing record(s)")
        
        # Commit changes
        conn.commit()
        
        # Verify migration
        print("\n→ Verifying migration...")
        cursor.execute("PRAGMA table_info(executions)")
        columns_after = [row[1] for row in cursor.fetchall()]
        
        assert "segments_json" in columns_after, "segments_json column missing"
        assert "audio_files_count" in columns_after, "audio_files_count column missing"
        print("  ✓ Migration verified")
        
        # Get statistics
        cursor.execute("SELECT COUNT(*) FROM executions")
        total_records = cursor.fetchone()[0]
        
        print()
        print("=" * 80)
        print("✅ MIGRATION SUCCESSFUL")
        print("=" * 80)
        print(f"Total records: {total_records}")
        print(f"New columns: segments_json, audio_files_count")
        print(f"Migration time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"\n❌ Migration failed: {e}")
        print("Database may be in inconsistent state.")
        print("Restore from backup if available.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # Check for --auto-confirm flag
    auto_confirm = "--auto-confirm" in sys.argv or "-y" in sys.argv
    migrate_database(auto_confirm=auto_confirm)

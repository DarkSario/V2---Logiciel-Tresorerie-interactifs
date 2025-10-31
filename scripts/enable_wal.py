#!/usr/bin/env python3
"""
Utility script to enable WAL (Write-Ahead Logging) mode on a SQLite database.

WAL mode provides better concurrency and reduces database locking issues.
This script can be used to enable WAL mode on any existing database.

Usage:
    python scripts/enable_wal.py [database_path]
    
If no database path is provided, it will use the default application database.
"""

import sqlite3
import os
import sys

# Add parent directory to path to import db module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.db import get_db_file

def enable_wal(db_path):
    """
    Enable WAL mode on the specified database.
    
    Args:
        db_path: Path to the SQLite database file
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not os.path.exists(db_path):
        print(f"✗ Error: Database file not found at {db_path}")
        return False
    
    print(f"Database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path, timeout=30.0)
        cursor = conn.cursor()
        
        # Check current journal mode
        cursor.execute("PRAGMA journal_mode;")
        current_mode = cursor.fetchone()[0]
        print(f"Current journal mode: {current_mode}")
        
        if current_mode.upper() == "WAL":
            print("✓ WAL mode is already enabled")
            conn.close()
            return True
        
        # Enable WAL mode
        print("→ Enabling WAL mode...")
        cursor.execute("PRAGMA journal_mode=WAL;")
        result = cursor.fetchone()[0]
        
        if result.upper() == "WAL":
            print(f"✓ Successfully enabled WAL mode")
        else:
            print(f"⚠ Warning: Expected WAL but got {result}")
        
        # Set synchronous to NORMAL for better performance
        print("→ Setting synchronous mode to NORMAL...")
        cursor.execute("PRAGMA synchronous=NORMAL;")
        print("✓ Synchronous mode set to NORMAL")
        
        # Display additional info
        cursor.execute("PRAGMA synchronous;")
        sync_mode = cursor.fetchone()[0]
        print(f"  Synchronous level: {sync_mode}")
        
        conn.close()
        print("\n✓ Database optimized for better concurrency")
        return True
        
    except sqlite3.OperationalError as e:
        error_msg = str(e).lower()
        if "database is locked" in error_msg:
            print(f"✗ Error: Database is currently locked by another process")
            print("  Please close all applications using the database and try again")
        else:
            print(f"✗ SQLite error: {e}")
        return False
        
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def main():
    """Main entry point for the script."""
    print("=" * 70)
    print("SQLite WAL Mode Enabler")
    print("=" * 70)
    print()
    
    # Determine database path
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        db_path = get_db_file()
        print(f"Using default database from configuration")
    
    success = enable_wal(db_path)
    
    print()
    print("=" * 70)
    if success:
        print("✓ OPERATION COMPLETED SUCCESSFULLY")
        print("=" * 70)
        sys.exit(0)
    else:
        print("✗ OPERATION FAILED")
        print("=" * 70)
        sys.exit(1)

if __name__ == "__main__":
    main()

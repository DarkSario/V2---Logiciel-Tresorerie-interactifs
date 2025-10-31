# Fix: DB write stability and safe migration for old databases

## Summary

This PR addresses database locking issues ("database is locked") and significantly improves database stability by implementing:

1. **Enhanced Migration Script** - Safe migration for adding `purchase_price` column with automatic backup
2. **Robust Database Operations** - Retry logic with exponential backoff for handling locked databases
3. **WAL Mode Support** - Write-Ahead Logging for better concurrency and reduced locking
4. **Backward Compatibility** - Graceful handling of old database schemas

## Changes Made

### 1. Enhanced `scripts/migrate_add_purchase_price.py`

**Features:**
- ✅ Automatic database backup (.bak) before migration
- ✅ Table existence detection with clear error messages  
- ✅ Idempotent operation (safe to run multiple times)
- ✅ Transaction-based operations with error handling
- ✅ Enables WAL mode and sets synchronous=NORMAL for better performance
- ✅ Clear exit codes and informative messages

### 2. Improved `lib/db_articles.py`

**Features:**
- ✅ Short-lived connections with 30-second timeout
- ✅ Retry/backoff wrapper for "database is locked" errors
- ✅ Exponential backoff (5 retries with increasing wait times)
- ✅ Backward compatibility with old database schemas
- ✅ All existing API functions maintained:
  - `get_all_articles()`
  - `get_article_by_id(article_id)`
  - `get_article_by_name(name)`
  - `create_article(...)`
  - `update_article_stock(article_id, stock)`
  - `update_article_purchase_price(article_id, purchase_price)`

### 3. New `scripts/enable_wal.py`

**Features:**
- ✅ Utility script to enable WAL mode on any database
- ✅ Can be used standalone: `python scripts/enable_wal.py [database_path]`
- ✅ Shows current journal mode and synchronous settings
- ✅ Clear status messages

## Installation & Usage Instructions

### For Users with Existing Databases

**⚠️ IMPORTANT: Before running the migration, please backup your database manually as an extra precaution!**

1. **Backup your database** (recommended):
   ```bash
   cp association.db association.db.backup
   ```

2. **Run the migration script**:
   ```bash
   python scripts/migrate_add_purchase_price.py
   ```

   The script will:
   - Create an automatic backup (.bak file)
   - Check if migration is needed
   - Add the `purchase_price` column if missing
   - Enable WAL mode for better performance
   - Display clear status messages

3. **Restart your application**:
   - The application will now benefit from improved database stability
   - No code changes needed in your existing workflows

### For New Installations

- No action needed! New databases created by `init_db()` already include all columns and optimizations.

### Optional: Enable WAL Mode on Other Databases

If you have other SQLite databases that could benefit from WAL mode:

```bash
python scripts/enable_wal.py path/to/your/database.db
```

## Technical Details

### What is WAL Mode?

Write-Ahead Logging (WAL) is a SQLite feature that:
- Allows multiple readers to access the database while a write is in progress
- Significantly reduces "database is locked" errors
- Improves overall concurrency and performance

### Retry Logic

The enhanced `db_articles.py` implements exponential backoff:
- Initial backoff: 0.1 seconds
- Maximum retries: 5
- Each retry doubles the wait time
- Clear warning messages when retries occur

### Backward Compatibility

The code gracefully handles old database schemas:
- Read operations work with or without `purchase_price` column
- Write operations detect missing columns and provide helpful messages
- No data loss or errors when running on old databases

## Rollback Instructions

If you need to rollback the migration:

1. **Stop the application**

2. **Restore from the automatic backup**:
   ```bash
   # Find the backup file (ends with .bak)
   ls -la *.bak
   
   # Restore (replace TIMESTAMP with actual timestamp)
   cp association.db.TIMESTAMP.bak association.db
   ```

3. **Restart the application**

## Testing Performed

- ✅ Migration tested on database without `purchase_price` column
- ✅ Migration tested on database with `purchase_price` column (idempotent)
- ✅ All database operations tested (read, create, update)
- ✅ Backward compatibility tested with old schema
- ✅ WAL mode enablement verified
- ✅ Retry logic manually tested with database locks

## Security Considerations

- Automatic backups prevent data loss
- Transaction-based operations ensure atomicity
- No credentials or sensitive data in code
- Clear error messages don't expose internal paths

## Files Changed

- `scripts/migrate_add_purchase_price.py` - Enhanced with backup, WAL, and better error handling
- `lib/db_articles.py` - Added retry logic and backward compatibility
- `scripts/enable_wal.py` - New utility script for WAL enablement

## Breaking Changes

None! This PR is 100% backward compatible.

## Performance Impact

Expected improvements:
- Reduced "database is locked" errors by 90%+
- Better concurrency with multiple users/processes
- Faster write operations with WAL mode
- Automatic retry handling prevents application crashes

## Future Improvements

Potential enhancements for future PRs:
- Configurable retry parameters via environment variables
- Metrics/logging for database operation performance
- Automated backup rotation (keeping last N backups)
- Database health check utility

---

**PR Type**: Bug Fix + Enhancement  
**Priority**: High (fixes production database locking issues)  
**Risk Level**: Low (backward compatible, automatic backups)

**Branch**: fix/db-stability

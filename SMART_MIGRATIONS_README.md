# Smart Migrations System

## Overview

The Smart Migrations system provides intelligent, safe database schema management through two complementary scripts:

1. **`scripts/analyze_modules_columns.py`** - SQL Schema Analyzer
2. **`scripts/update_db_structure.py`** - Database Structure Updater

## Features

### Analyzer (`analyze_modules_columns.py`)

**Strict SQL Identifier Extraction:**
- Uses regex pattern `^[A-Za-z_][A-Za-z0-9_]*$` to validate identifiers
- Extracts only valid SQL column/table names from code
- Avoids capturing UI text, code fragments, or invalid identifiers

**SQL Pattern Recognition:**
- Extracts from `INSERT INTO` statements
- Extracts from `UPDATE ... SET` statements
- Extracts from `SELECT ... FROM` statements
- Extracts from `CREATE TABLE` statements

**Output Generation:**
- `reports/SQL_SCHEMA_HINTS.md` - Human-readable markdown report
- `db/schema_hints.yaml` - Machine-readable YAML schema manifest
- Simple format with no dependencies, easy to edit manually

**Type Inference:**
- Automatically infers column types based on naming patterns
- Supports TEXT, INTEGER, REAL, and DATE types
- Uses pattern matching on column names (e.g., `prix_*` → REAL)

### Updater (`update_db_structure.py`)

**Smart Column Matching:**
- Fuzzy matching with configurable threshold (default 0.75)
- Case-insensitive column name comparison
- Detects similar columns (e.g., `parent_id` matches `parent`)

**Safe Migration Operations:**
1. **Timestamped Backups** - Always creates `association.db.YYYYMMDD_HHMMSS.bak`
2. **Validation** - Validates all column names against SQL identifier regex
3. **Fuzzy Rename** - Uses `ALTER TABLE RENAME COLUMN` when supported (SQLite 3.25+)
4. **Smart Add** - Adds column and copies data from fuzzy match if found
5. **Type Guessing** - Infers appropriate data types for new columns
6. **Rollback** - Automatic restoration from backup on errors

**Schema Loading:**
- Loads `db/schema_hints.yaml` if available
- Falls back to running analyzer if YAML missing
- Combines YAML hints with hardcoded REFERENCE_SCHEMA

**Reporting:**
- Generates detailed migration reports in `reports/migration_report_*.md`
- Logs all operations with timestamps
- Reports skipped invalid identifiers
- Shows column mappings and transformations

## Usage

### 1. Analyze Code for SQL Schema

```bash
python scripts/analyze_modules_columns.py
```

**Output:**
- `reports/SQL_SCHEMA_HINTS.md` - Detailed report of detected tables and columns
- `db/schema_hints.yaml` - YAML manifest for database updater

### 2. Update Database Structure

```bash
# Use default database (association.db)
python scripts/update_db_structure.py

# Specify custom database
python scripts/update_db_structure.py --db-path path/to/database.db

# Disable YAML hints (use only REFERENCE_SCHEMA)
python scripts/update_db_structure.py --no-yaml-hints
```

**What it does:**
1. Creates timestamped backup
2. Analyzes current database schema
3. Compares with expected schema (YAML + REFERENCE_SCHEMA)
4. Detects missing columns with fuzzy matching
5. Applies migrations safely
6. Optimizes database (WAL mode, ANALYZE)
7. Generates detailed migration report

## Migration Examples

### Example 1: Fuzzy Column Rename

**Scenario:** Code expects column `parent`, but database has `parent_id`

**Action:** 
```sql
ALTER TABLE categories RENAME COLUMN parent_id TO parent
```

**Result:** Column renamed, data preserved, no duplication

### Example 2: Add Column with Data Copy

**Scenario:** Column `categorie` expected, similar column `categorie_id` exists, but RENAME not supported

**Action:**
```sql
ALTER TABLE stock ADD COLUMN categorie TEXT DEFAULT '';
UPDATE stock SET categorie = categorie_id;
```

**Result:** New column added, data copied from similar column

### Example 3: Add New Column

**Scenario:** Column `description` expected, no similar column exists

**Action:**
```sql
ALTER TABLE events ADD COLUMN description TEXT DEFAULT '';
```

**Result:** New column added with inferred type and default value

## Validation & Safety

### SQL Identifier Validation

Both scripts use strict regex validation:
```regex
^[A-Za-z_][A-Za-z0-9_]*$
```

Invalid identifiers are:
- Reported in logs
- Skipped during migration
- Listed in migration reports

**Examples:**
- ✓ Valid: `user_id`, `firstName`, `_temp`, `column123`
- ✗ Invalid: `user-id`, `123column`, `user.name`
- ⚠ Reserved words (like `select`, `order`, `table`) are valid but will be quoted automatically

### Safety Mechanisms

1. **Backup Before Migration**
   - Timestamped backup created automatically
   - Format: `{database_name}.YYYYMMDD_HHMMSS.bak`
   - Original file never modified without backup
   - Backup location logged in report

2. **Transaction Rollback**
   - All migrations run in transaction
   - Automatic rollback on any error
   - Database restored from backup if needed

3. **Validation**
   - Column names validated before operations
   - SQL keywords properly quoted
   - Type compatibility checked

4. **Detailed Logging**
   - Every operation logged with timestamp
   - Migration report generated
   - Errors and warnings clearly marked

## Generated Files

### SQL_SCHEMA_HINTS.md

Human-readable markdown report showing:
- Total tables detected
- Summary by table (column count, file references)
- Detailed table schemas with inferred types
- Files where each table is referenced
- List of skipped invalid identifiers

### schema_hints.yaml

Machine-readable YAML manifest:
```yaml
schema_version: "1.0"
generated_by: "analyze_modules_columns.py"

tables:
  table_name:
    expected_columns:
      column_name:
        type: TEXT|INTEGER|REAL|DATE
        inferred: true

manual_overrides: {}
```

You can manually add overrides:
```yaml
manual_overrides:
  table_name:
    column_aliases:
      old_name: new_name
    forced_types:
      column_name: REAL
```

### migration_report_*.md

Detailed migration report including:
- Migration status (SUCCESS/FAILED)
- Environment information
- Summary of changes
- Detailed changes by table
- Column mappings (renames/copies)
- Skipped invalid identifiers
- Error messages (if any)
- Complete migration log

## Best Practices

1. **Run Analyzer First**
   - Always run analyzer before updater
   - Review generated reports
   - Manually adjust schema_hints.yaml if needed

2. **Test on Copy**
   - Test migrations on database copy first
   - Verify results before production use
   - Check migration reports carefully

3. **Backup Management**
   - Keep multiple backups
   - Test backup restoration periodically
   - Clean old backups after verification

4. **Schema Review**
   - Review SQL_SCHEMA_HINTS.md for accuracy
   - Check for unwanted/invalid identifiers
   - Verify inferred types are correct

5. **Manual Overrides**
   - Use manual_overrides in YAML for special cases
   - Document custom mappings
   - Commit schema_hints.yaml to version control

## Troubleshooting

### Issue: Invalid identifiers detected

**Solution:** Check SQL_SCHEMA_HINTS.md "Identifiants Invalides Ignorés" section. These are typically:
- SQL keywords without proper quoting
- Typos in SQL queries
- UI text mistakenly captured
- Code variables mixed with SQL

### Issue: Fuzzy match incorrect

**Solution:** Add manual override in schema_hints.yaml:
```yaml
manual_overrides:
  table_name:
    column_aliases:
      actual_name: expected_name
```

### Issue: Type inference wrong

**Solution:** Override type in schema_hints.yaml:
```yaml
manual_overrides:
  table_name:
    forced_types:
      column_name: INTEGER
```

### Issue: Migration failed

**Solution:**
1. Check migration report in `reports/migration_report_failed_*.md`
2. Database automatically restored from backup
3. Fix reported issues
4. Run migration again

## Development

### Adding New Type Patterns

Edit `analyze_modules_columns.py`:
```python
self.type_patterns = {
    'REAL': [
        r'(prix|montant|solde)(_\w+)?$',
        # Add new patterns here
    ],
    # ... other types
}
```

### Adjusting Fuzzy Threshold

To change the fuzzy matching threshold, modify the `DatabaseMigrator` initialization in `update_db_structure.py`:
```python
# In the main() function, change:
migrator = DatabaseMigrator(args.db_path, use_yaml_hints=not args.no_yaml_hints, fuzzy_threshold=0.8)
```

Lower values = stricter matching (fewer false positives)
Higher values = looser matching (more potential matches)

## Integration with CI/CD

### Pre-commit Hook

```bash
#!/bin/bash
# Run analyzer to detect schema changes
python scripts/analyze_modules_columns.py
git add db/schema_hints.yaml reports/SQL_SCHEMA_HINTS.md
```

### Deployment Script

```bash
#!/bin/bash
# Safe migration during deployment
python scripts/update_db_structure.py --db-path production.db
if [ $? -ne 0 ]; then
    echo "Migration failed, rollback applied"
    exit 1
fi
```

## Requirements

- Python 3.9+
- SQLite 3.25+ recommended (for RENAME COLUMN support; older versions work but will use ADD+COPY instead)
- Core functionality has no external dependencies (uses standard library)
- Optional: PyYAML for YAML loading (falls back to compat_yaml module if PyYAML not available)

## License

Part of the V2 Logiciel Trésorerie Interactifs project.

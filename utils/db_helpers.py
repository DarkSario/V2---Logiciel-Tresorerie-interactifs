"""
Database helper utilities.

This module provides utility functions for working with database results,
particularly for safely handling sqlite3.Row objects.
"""


def row_to_dict(row):
    """
    Convert sqlite3.Row to dict for safe .get() access.
    
    sqlite3.Row objects support dictionary-style access (row['column']) but
    lack the .get() method that dicts have for optional fields with defaults.
    This function converts a Row to a dict to enable .get() usage.
    
    Args:
        row: sqlite3.Row object or None
        
    Returns:
        dict or None: Dictionary representation of the row, or None if input is None
        
    Example:
        >>> row = cursor.execute("SELECT * FROM table").fetchone()
        >>> row_dict = row_to_dict(row)
        >>> value = row_dict.get('optional_column', 'default')
    """
    if row is None:
        return None
    return dict(row)


def rows_to_dicts(rows):
    """
    Convert list of sqlite3.Row objects to list of dicts.
    
    This is a batch version of row_to_dict() for converting multiple rows.
    
    Args:
        rows: list of sqlite3.Row objects
        
    Returns:
        list of dicts: List of dictionary representations
        
    Example:
        >>> rows = cursor.execute("SELECT * FROM table").fetchall()
        >>> dicts = rows_to_dicts(rows)
        >>> for d in dicts:
        >>>     print(d.get('optional_column', 'N/A'))
    """
    return [dict(row) for row in rows]


def row_get_safe(row, key, default=None):
    """
    Safe accessor for sqlite3.Row that returns default value when column is absent.
    
    This function provides a .get()-like interface directly on Row objects without
    needing to convert the entire row to a dict. Useful when only accessing one
    or two optional fields.
    
    Note: sqlite3.Row raises IndexError (not KeyError) when accessing missing
    columns, whether using string keys or integer indices.
    
    Args:
        row: sqlite3.Row object
        key: column name (string) or index (integer) to access
        default: value to return if column doesn't exist
        
    Returns:
        row[key] if column exists, default otherwise
        
    Example:
        >>> row = cursor.execute("SELECT * FROM table").fetchone()
        >>> name = row_get_safe(row, 'name', 'Unknown')
        >>> first_col = row_get_safe(row, 0, None)
    """
    try:
        return row[key]
    except IndexError:
        return default

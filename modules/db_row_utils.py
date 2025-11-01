"""
Database row utility functions for safe sqlite3.Row conversions.

This module provides utility functions to safely convert sqlite3.Row objects
to dictionaries, enabling the use of .get() method for optional field access.

Functions:
    _row_to_dict: Convert a single sqlite3.Row to dict
    _rows_to_dicts: Convert a list of sqlite3.Row objects to list of dicts
"""

from typing import Any, Dict, List, Optional
import sqlite3


def _row_to_dict(row: Optional[sqlite3.Row]) -> Optional[Dict[str, Any]]:
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
        >>> row_dict = _row_to_dict(row)
        >>> value = row_dict.get('optional_column', 'default')
    """
    if row is None:
        return None
    
    # Handle both sqlite3.Row and tuple types
    if isinstance(row, dict):
        # Already a dict, return as-is
        return row
    
    try:
        # Convert Row to dict
        return dict(row)
    except (TypeError, ValueError) as e:
        # Fallback for other sequence types (tuples, etc.)
        # This shouldn't happen in normal sqlite3 usage, but provides safety
        if hasattr(row, '__iter__') and not isinstance(row, (str, bytes)):
            # If it's a tuple and we don't have column names, return None
            # In practice, sqlite3.Row should always work with dict()
            return None
        raise TypeError(f"Cannot convert {type(row)} to dict: {e}")


def _rows_to_dicts(rows: List[sqlite3.Row]) -> List[Dict[str, Any]]:
    """
    Convert list of sqlite3.Row objects to list of dicts.
    
    This is a batch version of _row_to_dict() for converting multiple rows.
    Filters out None values automatically.
    
    Args:
        rows: list of sqlite3.Row objects
        
    Returns:
        list of dicts: List of dictionary representations
        
    Example:
        >>> rows = cursor.execute("SELECT * FROM table").fetchall()
        >>> dicts = _rows_to_dicts(rows)
        >>> for d in dicts:
        >>>     print(d.get('optional_column', 'N/A'))
    """
    if not rows:
        return []
    
    result = []
    for row in rows:
        converted = _row_to_dict(row)
        if converted is not None:
            result.append(converted)
    
    return result

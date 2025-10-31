import re
from typing import Any, Dict, Iterable

def is_email(email):
    """
    Vérifie si la chaîne est un email valide (format simple, sans DNS check).
    """
    if not email or not isinstance(email, str):
        return False
    # Expression régulière simple pour les emails valides
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None

def is_required(value):
    """
    Retourne True si la valeur est présente et non vide.
    """
    return bool(value and str(value).strip())
    
def is_number(val):
    try:
        float(val)
        return True
    except (ValueError, TypeError):
        return False

def is_valid_string(s: Any, allow_empty: bool = False) -> bool:
    if not isinstance(s, str):
        return False
    if not allow_empty and s.strip() == '':
        return False
    return True

def validate_record(schema: Dict[str, type], record: Dict[str, Any]) -> bool:
    """Basic schema validation: checks presence and type of keys. Returns True if valid."""
    for k, t in schema.items():
        if k not in record:
            return False
        if not isinstance(record[k], t):
            return False
    return True

def sanitize_string(s: str) -> str:
    # Minimal sanitization: strip control chars and trim
    return ''.join(ch for ch in s if ch.isprintable()).strip()
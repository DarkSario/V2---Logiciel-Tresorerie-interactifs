import re

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
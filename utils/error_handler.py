import traceback
from utils.app_logger import get_logger
import tkinter as tk
from tkinter import messagebox

logger = get_logger("error_handler")

def handle_exception(e, user_msg="Une erreur est survenue."):
    """
    Centralise la gestion des exceptions :
    - Loggue l'exception (trace complète dans logs)
    - Retourne un message utilisateur prêt à afficher
    """
    tb_str = traceback.format_exc()
    logger.error(f"{user_msg}\nException: {e}\nTraceback:\n{tb_str}")
    return user_msg
    
def handle_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as ex:
            tb = traceback.format_exc()
            logger.error(f"Erreur: {ex}\nTraceback:\n{tb}")
            messagebox.showerror("Erreur", f"{ex}\n\n{tb}")
    return wrapper

def safe_call(func, *args, user_msg="Une erreur est survenue.", **kwargs):
    """
    Exécute une fonction de façon sécurisée :
    - Si tout va bien, retourne le résultat
    - Si exception, loggue et retourne None + affiche un message utilisateur
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        handle_exception(e, user_msg)
        return None
"""
These functions facilitate the running of app.py
"""
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from flask import redirect, render_template, request, session


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def pwd_match(password: str, confirmation: str) -> bool:
    """ 
    Returns True if password and confirmation are the same and are not empty
    """
    # password should not be empty
    if not password or not confirmation:
        return False

    # password should match confirmation
    if password != confirmation:
        return False

    return True


def get_hash_pwd(password: str):
    """ Returns hashed version of string password """
    hash_pwd = generate_password_hash(
        password, method='pbkdf2:sha256', salt_length=8)
    return hash_pwd


def check_hash_pwd(hash_pwd, password) -> bool:
    """ Returns True if password is the same as hash password, False otherwise """
    return check_password_hash(hash_pwd, password)

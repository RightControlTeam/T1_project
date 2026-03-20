# user/validation.py

from re import match


def is_username_valid(username: str) -> bool:
    if not (5 <= len(username) < 25):
        return False

    if not match(r'^\w+$', username):
        return False

    if match(r'^[0-9_]', username):
        return False

    return True


def is_password_valid(password: str) -> bool:
    if not (8 <= len(password) <= 40):
        return False

    return True

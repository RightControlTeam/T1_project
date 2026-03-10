#security/password.py


from bcrypt import hashpw, gensalt, checkpw


def get_password_hash(plain_password) -> str:
    pwd_bytes = plain_password.encode("utf8")
    salt = gensalt()
    return hashpw(pwd_bytes, salt).decode("utf8")


def verify_password(plain_password, hashed_password) -> bool:
    return checkpw(
        plain_password.encode('utf8'),
        hashed_password.encode("utf8")
    )
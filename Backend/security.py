#security.py


from datetime import datetime, timedelta, UTC
from config import settings
from bcrypt import hashpw, gensalt, checkpw
from jwt import encode
from user.schemas import LoginResponse


def get_password_hash(plain_password) -> str:
    pwd_bytes = plain_password.encode("utf8")
    salt = gensalt()
    return hashpw(pwd_bytes, salt).decode("utf8")


def verify_password(plain_password, hashed_password) -> bool:
    return checkpw(
        plain_password.encode('utf8'),
        hashed_password.encode("utf8")
    )


def create_jwt(user_id: int) -> dict:
    payload = {"sub": user_id}

    exp_time_delta = timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    exp_time = datetime.now(UTC) + exp_time_delta
    exp_time = int(exp_time.timestamp())

    return {
        "jwt": encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
        ),
        "exp_time": exp_time
    }


def generate_login_response(user_id) -> LoginResponse:
    jwt = create_jwt(user_id)

    return LoginResponse(
        jwt = jwt["jwt"],
        token_type = "bearer",
        jwt_exp_time = jwt["exp_time"]
    )
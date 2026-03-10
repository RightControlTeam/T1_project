#security/token.py


from datetime import datetime, timedelta, UTC
from config import settings
from jwt import encode, decode, PyJWTError
from user.schemas import LoginResponse
from fastapi import HTTPException


def generate_jwt(user_id: int) -> dict:
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
    jwt = generate_jwt(user_id)

    return LoginResponse(
        jwt = jwt["jwt"],
        token_type = "bearer",
        jwt_exp_time = jwt["exp_time"]
    )


def decode_jwt(token: str) -> dict:
    try:
        return decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=["HS256"]
        )
    except PyJWTError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token: {str(e)}",
        )
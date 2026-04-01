#security/token.py


from datetime import datetime, timedelta, UTC
from jwt import encode, decode, PyJWTError
from fastapi import HTTPException
from pydantic import BaseModel

from core.config import settings


class JWTPayload(BaseModel):
    sub: str
    exp: int

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    admin_level: int


def generate_login_response(user_id: int, admin_level: int) -> TokenResponse:
    exp_time_delta: timedelta = timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    exp_time: datetime = datetime.now(UTC) + exp_time_delta
    exp_time_int: int = int(exp_time.timestamp())

    payload: JWTPayload = JWTPayload(
        sub = str(user_id),
        exp = exp_time_int
    )

    token: str = encode(
        payload.model_dump(),
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return TokenResponse(
        access_token= token,
        token_type = "Bearer",
        expires_in = settings.JWT_EXPIRE_MINUTES * 60,
        admin_level = admin_level
    )



def decode_jwt(token: str) -> JWTPayload:
    try:
        payload: dict = decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=settings.JWT_ALGORITHM
        )
        return JWTPayload(**payload)

    except PyJWTError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token: {str(e)}",
        )
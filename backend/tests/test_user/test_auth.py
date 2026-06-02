import pytest
from httpx import AsyncClient

from core.config import settings


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    """Успешная регистрация"""
    response = await client.post("/user/register-user", json={
        "username": "newuser",
        "password": "ValidPass123",
    })
    assert response.status_code == 201
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_register_duplicate(client: AsyncClient):
    """Регистрация с существующим username"""
    payload = {
        "username": "unique_user_123",
        "password": "StrongPassword123",
    }

    first_res = await client.post("/user/register-user", json=payload)
    assert first_res.status_code == 201

    second_res = await client.post("/user/register-user", json=payload)
    assert second_res.status_code == 409

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user):
    """Успешный вход"""
    response = await client.post("/user/login/", data={
        "username": "testuser",
        "password": "TestPass123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, test_user):
    """ТВход с неверным паролем"""
    response = await client.post("/user/login/", data={
        "username": "testuser",
        "password": "WrongPass123"
    })
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """ Вход с несуществующим пользователем"""
    response = await client.post("/user/login/", data={
        "username": "ghostuser",
        "password": "SomePass123"
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_invalid_username(client: AsyncClient):
    """Невалидный username при логине """
    response = await client.post("/user/login/", data={
        "username": "ab",
        "password": "ValidPass123",
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Username validation error"


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient):
    """Невалидный пароль при логине """
    response = await client.post("/user/login/", data={
        "username": "validuser",
        "password": "short",
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Password validation error"


@pytest.mark.asyncio
async def test_register_invalid_username(client: AsyncClient):
    """Тест регистрации с невалидным username"""
    response = await client.post("/user/register-user", json={
        "username": "a",
        "password": "ValidPass123",
    })
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_register_invalid_password(client: AsyncClient):
    """Тест регистрации с невалидным паролем"""
    response = await client.post("/user/register-user", json={
        "username": "validuser",
        "password": "short",
    })
    assert response.status_code == 422

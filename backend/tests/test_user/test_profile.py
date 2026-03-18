import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_profile_with_token(client: AsyncClient, test_user):
    """Получение профиля с токеном"""
    user, token = test_user
    response = await client.get(
        "/user/profile/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"

@pytest.mark.asyncio
async def test_profile_without_token(client: AsyncClient):
    """Получение профиля без токена"""
    response = await client.get("/user/profile/")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_users_list(client: AsyncClient, test_user):
    """Получение списка пользователей"""
    user, token = test_user
    response = await client.get(
        "/user/list/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_get_profile_no_token(client: AsyncClient):
    """Тест получения профиля без токена"""
    response = await client.get("/user/profile/")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_profile_invalid_token(client: AsyncClient):
    """Тест получения профиля с невалидным токеном"""
    response = await client.get(
        "/user/profile/",
        headers={"Authorization": "Bearer invalid.token.here"}
    )
    assert response.status_code == 401
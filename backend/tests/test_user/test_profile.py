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
        "/user/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_get_profile_invalid_token(client: AsyncClient):
    """Тест получения профиля с невалидным токеном"""
    response = await client.get(
        "/user/profile/",
        headers={"Authorization": "Bearer invalid.token.here"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_user(client: AsyncClient, test_user):
    """Обновление профиля """
    _, token = test_user
    response = await client.put(
        "/user/",
        json={"username": "updateduser", "password": "NewPass12345"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["username"] == "updateduser"


@pytest.mark.asyncio
async def test_delete_me(client: AsyncClient, test_user):
    """Деактивация своего аккаунта """
    _, token = test_user
    response = await client.delete(
        "/user/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_register_admin_by_creator(client: AsyncClient, creator_token_headers):
    """Регистрация админа creator"""
    response = await client.post(
        "/user/register-admin",
        json={"username": "newadmin", "password": "AdminPass123"},
        headers=creator_token_headers,
    )
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_creator_delete_fake_user(client: AsyncClient, test_creator):
    """Удаление несуществующего пользователя"""
    _, token = test_creator
    response = await client.delete(
        "/user/99999",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404

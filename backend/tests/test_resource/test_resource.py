from datetime import datetime, timedelta
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_resource_admin(client: AsyncClient, test_admin):
    """Админ создает ресурс"""
    admin, token = test_admin
    response = await client.post(
        "/resource/",
        json={
            "name": "New Projector",
            "type": "equipment",
            "is_active": True
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "New Projector"

@pytest.mark.asyncio
async def test_create_resource_user(client: AsyncClient, test_user):
    """Обычный пользователь НЕ может создать ресурс"""
    user, token = test_user
    response = await client.post(
        "/resource/",
        json={"name": "Test", "type": "room"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_get_resources(client: AsyncClient, test_user, test_resource):
    """Получение списка ресурсов"""
    user, token = test_user
    response = await client.get(
        "/resource/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_get_resources_filter_by_type(client: AsyncClient, test_admin):
    """Фильтр списка по type """
    _, token = test_admin
    headers = {"Authorization": f"Bearer {token}"}

    await client.post(
        "/resource/",
        json={"name": "Room A", "type": "room", "is_active": True},
        headers=headers,
    )
    await client.post(
        "/resource/",
        json={"name": "Projector", "type": "equipment", "is_active": True},
        headers=headers,
    )

    response = await client.get("/resource/?type=room", headers=headers)
    assert response.status_code == 200
    items = response.json()
    assert len(items) >= 1
    assert all(item["type"] == "room" for item in items)


@pytest.mark.asyncio
async def test_get_resource_by_id(client: AsyncClient, test_user, test_resource):
    """Получение ресурса по ID"""
    user, token = test_user
    response = await client.get(
        f"/resource/{test_resource.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["id"] == test_resource.id

@pytest.mark.asyncio
async def test_update_resource_admin(client: AsyncClient, test_admin, test_resource):
    """Админ обновляет ресурс"""
    admin, token = test_admin
    response = await client.put(
        f"/resource/{test_resource.id}",
        json={"name": "Updated Name"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"


@pytest.mark.asyncio
async def test_update_resource_success(client: AsyncClient, test_admin, test_resource):
    """Тест update"""
    _, token = test_admin
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.put(
        f"/resource/{test_resource.id}",
        json={
            "name": "Room",
            "description": "Updated description",
            "type": "room",
            "is_active": False,
        },
        headers=headers,
    )
    assert response.status_code == 200

    get_response = await client.get(
        f"/resource/{test_resource.id}",
        headers=headers,
    )
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["name"] == "Room"
    assert data["description"] == "Updated description"
    assert data["type"] == "room"
    assert data["is_active"] is False


@pytest.mark.asyncio
async def test_update_resource_by_user(client: AsyncClient, test_user, test_resource):
    """Обычный пользователь не может обновить ресурс"""
    _, token = test_user
    response = await client.put(
        f"/resource/{test_resource.id}",
        json={"name": "Hacked Name"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_resource_admin(client: AsyncClient, test_admin, test_resource):
    """Админ удаляет ресурс"""
    admin, token = test_admin
    response = await client.delete(
        f"/resource/{test_resource.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_resource_not_found(client: AsyncClient, test_admin, test_resource):
    """После удаления ресурс недоступен """
    _, token = test_admin
    headers = {"Authorization": f"Bearer {token}"}

    delete_response = await client.delete(
        f"/resource/{test_resource.id}",
        headers=headers,
    )
    assert delete_response.status_code == 204

    get_response = await client.get(
        f"/resource/{test_resource.id}",
        headers=headers,
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_get_nonexistent_resource(client: AsyncClient, test_user):
    """Запрос несуществующего ресурса возвращает 404"""
    user, token = test_user
    response = await client.get(
        "/resource/99999",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Resource not found"


@pytest.mark.asyncio
async def test_update_nonexistent_resource(client: AsyncClient, test_admin):
    """Попытка обновить ресурс, которого нет в базе"""
    admin, token = test_admin
    non_existent_id = 9999

    response = await client.put(
        f"/resource/{non_existent_id}",
        json={"name": "Ghost Resource"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_nonexistent_resource(client: AsyncClient, test_admin):
    """Попытка удалить ресурс, которого нет в базе"""
    admin, token = test_admin
    non_existent_id = 9999

    response = await client.delete(
        f"/resource/{non_existent_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_create_schedule_resource_not_found(client: AsyncClient, test_admin):
    """Расписание для несуществующего ресурса"""
    _, token = test_admin
    response = await client.post(
        "/resource/99999/schedule",
        json={"day_of_week": 0, "start_time": "10:00:00", "end_time": "12:00:00"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_schedule_complex_merge(client: AsyncClient, test_admin, test_resource):
    """Один новый интервал объединяет два существующих"""
    _, token = test_admin
    headers = {"Authorization": f"Bearer {token}"}

    for start, end in [("10:00:00", "12:00:00"), ("14:00:00", "16:00:00")]:
        await client.post(
            f"/resource/{test_resource.id}/schedule",
            json={"day_of_week": 1, "start_time": start, "end_time": end},
            headers=headers
        )

    res = await client.post(
        f"/resource/{test_resource.id}/schedule",
        json={"day_of_week": 1, "start_time": "11:00:00", "end_time": "15:00:00"},
        headers=headers
    )
    assert res.status_code == 201

    get_res = await client.get(f"/resource/{test_resource.id}", headers=headers)
    schedules = get_res.json()["schedules"]

    assert len(schedules) == 1
    assert schedules[0]["start_time"] == "10:00:00"
    assert schedules[0]["end_time"] == "16:00:00"


@pytest.mark.asyncio
async def test_delete_resource_with_active_bookings(client: AsyncClient, test_admin, test_user):
    _, admin_token = test_admin
    _, user_token = test_user

    res = await client.post("/resource/",
                            json={"name": "Test", "type": "room"},
                            headers={"Authorization": f"Bearer {admin_token}"})
    resource_id = res.json()["id"]

    await client.post(f"/resource/{resource_id}/schedule",
                      json={"day_of_week": 0, "start_time": "00:00:00", "end_time": "23:59:59"},
                      headers={"Authorization": f"Bearer {admin_token}"})

    tomorrow = (datetime.now() + timedelta(days=1)).isoformat()
    await client.post("/booking/",
                      json={"resource_id": resource_id, "start_time": tomorrow, "end_time": tomorrow},
                      headers={"Authorization": f"Bearer {user_token}"})

    delete_res = await client.delete(f"/resource/{resource_id}",
                                     headers={"Authorization": f"Bearer {admin_token}"})

    assert delete_res.status_code == 204
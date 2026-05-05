import pytest
from httpx import AsyncClient
from fastapi import status

@pytest.mark.asyncio
async def test_admin_full_flow(client: AsyncClient, test_admin):
    """Полный цикл работы админа"""
    admin_user, token = test_admin

    create = await client.post(
        "/resource/",
        json={"name": "Boss Room", "type": "room"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create.status_code == 201
    resource_id = create.json()["id"]

    get = await client.get(
        f"/resource/{resource_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get.status_code == 200

    delete = await client.delete(
        f"/resource/{resource_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert delete.status_code == 204

@pytest.mark.asyncio
async def test_admin_creates_resource(client: AsyncClient, admin_token_headers):
    resource_data = {"name": "аудитория 1", "type": "room", "description": "аудитория 1"}
    response = await client.post("/resource/", json=resource_data, headers=admin_token_headers)
    assert response.status_code == status.HTTP_201_CREATED
    resource_id = response.json()["id"]

    schedule_data = {
        "work_start": "09:00:00",
        "work_end": "18:00:00"
    }
    response = await client.post(f"/resource/{resource_id}/schedule", json=schedule_data, headers=admin_token_headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["work_start"] == "09:00:00"


@pytest.mark.asyncio
async def test_booking_overlap_conflict(client: AsyncClient, user_token_headers, created_resource):
    resource_id = created_resource["id"]

    booking_1 = {
        "resource_id": resource_id,
        "start_time": "2026-05-20T10:00:00",
        "end_time": "2026-05-20T12:00:00"
    }
    res1 = await client.post("/booking/", json=booking_1, headers=user_token_headers)
    assert res1.status_code == status.HTTP_201_CREATED

    booking_2 = {
        "resource_id": resource_id,
        "start_time": "2026-05-20T11:00:00",
        "end_time": "2026-05-20T13:00:00"
    }
    res2 = await client.post("/booking/", json=booking_2, headers=user_token_headers)

    assert res2.status_code == status.HTTP_409_CONFLICT
    assert "already booked" in res2.json()["detail"]
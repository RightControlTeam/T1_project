import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta


@pytest.mark.asyncio
async def test_booking_full_cycle(client: AsyncClient, test_user, test_resource, test_admin):
    """Бронирование и потом попытка другим забронировать"""
    _, admin_token = test_admin
    _, user_token = test_user

    await client.post(
        f"/resource/{test_resource.id}/schedule",
        json={"day_of_week": 0, "start_time": "08:00:00", "end_time": "20:00:00"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    today = datetime.now()
    next_monday = today + timedelta(days=(0 - today.weekday() + 7) % 7)
    start_time = next_monday.replace(hour=10, minute=0, second=0).isoformat()
    end_time = next_monday.replace(hour=12, minute=0, second=0).isoformat()

    res = await client.post(
        "/booking/",
        json={"resource_id": test_resource.id, "start_time": start_time, "end_time": end_time},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert res.status_code == 201
    booking_id = res.json()["id"]

    res_overlap = await client.post(
        "/booking/",
        json={"resource_id": test_resource.id, "start_time": start_time, "end_time": end_time},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res_overlap.status_code == 409
    assert "overlaps" in res_overlap.json()["detail"]


@pytest.mark.asyncio
async def test_booking_outside_schedule(client: AsyncClient, test_user, test_resource, test_admin):
    """Бронирование в нерабочее время"""
    _, admin_token = test_admin
    _, user_token = test_user

    await client.post(
        f"/resource/{test_resource.id}/schedule",
        json={"day_of_week": 0, "start_time": "15:00:00", "end_time": "18:00:00"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    today = datetime.now()
    next_monday = today + timedelta(days=(0 - today.weekday() + 7) % 7)

    bad_start = next_monday.replace(hour=10, minute=0).isoformat()
    bad_end = next_monday.replace(hour=11, minute=0).isoformat()

    res = await client.post(
        "/booking/",
        json={"resource_id": test_resource.id, "start_time": bad_start, "end_time": bad_end},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert res.status_code == 409
    assert "match schedule" in res.json()["detail"]


@pytest.mark.asyncio
async def test_booking_edge_cases(client: AsyncClient, test_user, test_resource, test_admin):
    """Бронирование на границе расписания"""
    _, admin_token = test_admin
    _, user_token = test_user

    await client.post(
        f"/resource/{test_resource.id}/schedule",
        json={"day_of_week": 0, "start_time": "15:00:00", "end_time": "18:00:00"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    today = datetime.now()
    next_monday = today + timedelta(days=(0 - today.weekday() + 7) % 7)

    start_dt = next_monday.replace(hour=17, minute=0, second=0, microsecond=0)
    end_dt = next_monday.replace(hour=18, minute=0, second=0, microsecond=0)

    res_ok = await client.post(
        "/booking/",
        json={
            "resource_id": test_resource.id,
            "start_time": start_dt.isoformat(),
            "end_time": end_dt.isoformat()
        },
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert res_ok.status_code == 201

@pytest.mark.asyncio
async def test_booking_non_existent_resource(client: AsyncClient, test_user):
    _, token = test_user
    tomorrow = datetime.now() + timedelta(days=1)
    res = await client.post("/booking/",
                             json={
                                 "resource_id": 99999,
                                 "start_time": tomorrow.isoformat(),
                                 "end_time": (tomorrow + timedelta(hours=1)).isoformat()
                             },
                             headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_cancel_booking_success(client: AsyncClient, test_user, test_resource, test_admin):
    """Тест успешной отмены бронирования """
    _, admin_token = test_admin
    user, user_token = test_user

    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_weekday = tomorrow.weekday()

    await client.post(
        f"/resource/{test_resource.id}/schedule",
        json={
            "day_of_week": tomorrow_weekday,
            "start_time": "00:00:00",
            "end_time": "23:59:59"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    start_dt = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
    end_dt = tomorrow.replace(hour=11, minute=0, second=0, microsecond=0)

    res = await client.post(
        "/booking/",
        json={
            "resource_id": test_resource.id,
            "start_time": start_dt.isoformat(),
            "end_time": end_dt.isoformat()
        },
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert res.status_code == 201
    booking_id = res.json()["id"]

    cancel_res = await client.delete(
        f"/booking/{booking_id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert cancel_res.status_code == 204

    check_res = await client.get(
        f"/booking/",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    cancelled_booking = next(b for b in check_res.json() if b["id"] == booking_id)
    assert cancelled_booking["is_cancelled"] is True
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_schedule(client: AsyncClient, test_admin, test_resource):
    """Проверка создания расписания и слияния пересекающихся интервалов"""
    _, token = test_admin
    headers = {"Authorization": f"Bearer {token}"}

    res1 = await client.post(
        f"/resource/{test_resource.id}/schedule",
        json={"day_of_week": 0, "start_time": "10:00:00", "end_time": "14:00:00"},
        headers=headers
    )
    assert res1.status_code == 201

    res2 = await client.post(
        f"/resource/{test_resource.id}/schedule",
        json={"day_of_week": 0, "start_time": "12:00:00", "end_time": "16:00:00"},
        headers=headers
    )
    assert res2.status_code == 201

    get_res = await client.get(f"/resource/{test_resource.id}", headers=headers)
    schedules = get_res.json()["schedules"]

    assert len(schedules) == 1
    assert schedules[0]["start_time"] == "10:00:00"
    assert schedules[0]["end_time"] == "16:00:00"


@pytest.mark.asyncio
async def test_schedule_wrong_day(client: AsyncClient, test_admin, test_resource):
    """Создание расписания на разные дни"""
    _, token = test_admin
    headers = {"Authorization": f"Bearer {token}"}

    await client.post(
        f"/resource/{test_resource.id}/schedule",
        json={"day_of_week": 0, "start_time": "10:00:00", "end_time": "12:00:00"},
        headers=headers
    )
    await client.post(
        f"/resource/{test_resource.id}/schedule",
        json={"day_of_week": 1, "start_time": "10:00:00", "end_time": "12:00:00"},
        headers=headers
    )

    get_res = await client.get(f"/resource/{test_resource.id}", headers=headers)
    assert len(get_res.json()["schedules"]) == 2
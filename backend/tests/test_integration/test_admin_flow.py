import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_admin_full_flow(client: AsyncClient):
    """Полный цикл работы админа"""

    reg = await client.post("/user/register/", json={
        "username": "bigboss",
        "password": "BigBoss123",
        "is_admin": True
    })
    assert reg.status_code == 201
    token = reg.json()["access_token"]

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
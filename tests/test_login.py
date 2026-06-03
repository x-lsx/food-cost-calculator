import pytest
import uuid

@pytest.mark.asyncio
async def test_login_user(client):

    payload = {
        "email": "asd@asd.asd",
        "password": "asd123",
    }

    response = await client.post(
        "/api/v1/auth/login",
        json=payload
    )

    assert response.status_code == 200
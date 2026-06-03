import pytest


@pytest.mark.asyncio
async def test_docs_available(client):

    response = await client.get("/api/docs")

    assert response.status_code == 200
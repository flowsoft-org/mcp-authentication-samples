import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
import json
from server import app, mcp, tell_joke, jokes

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client

@pytest.mark.asyncio
async def test_sse_endpoint_no_auth(client):
    """Test that SSE endpoint requires authentication"""
    response = await client.get("/sse")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
    assert "WWW-Authenticate" in response.headers

@pytest.mark.asyncio
async def test_sse_endpoint_invalid_token(client):
    """Test that SSE endpoint rejects invalid tokens"""
    headers = {"Authorization": "Bearer invalid_token"}
    response = await client.get("/sse", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid authentication credentials"}

# @pytest.mark.asyncio
# async def test_sse_endpoint_valid_token(client):
#     """Test that SSE endpoint accepts valid token"""
#     headers = {"Authorization": "Bearer valid_token"}
#     async with client.stream('GET', "/sse", headers=headers, timeout=1.0) as response:
#         assert response.status_code == 200
#         assert response.headers["content-type"] == "text/event-stream"
#         # Read just the first chunk to verify the connection works
#         chunk = await response.aread(1024)
#         assert chunk  # Verify we got some data

@pytest.mark.asyncio
async def test_joke_tool_registration():
    """Test that the joke tool is properly registered with MCP"""
    tools = await mcp.list_tools()
    tool_names = [tool.name for tool in tools]
    assert "tell_joke" in tool_names
    tool = next(t for t in tools if t.name == "tell_joke")
    assert tool.description == "Get a programming joke"

def test_joke_cycling():
    """Test that jokes cycle through the list"""
    received_jokes = set()
    for _ in range(len(jokes) * 2):  # Call twice as many times as we have jokes
        joke = tell_joke()
        received_jokes.add(joke)
    assert received_jokes == set(jokes)  # All jokes should have been seen
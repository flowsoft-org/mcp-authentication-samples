from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
# Serve a specific file at /.well-known/oauth-protected-resource
from fastapi.responses import FileResponse
from fastmcp import FastMCP
from fastmcp.server.auth import BearerAuthProvider
from itertools import cycle
import uvicorn
import os

# Define the authentication provider for token validation
auth = BearerAuthProvider(
    jwks_uri="https://login.microsoftonline.com/<ENTRATENANTID>/discovery/v2.0/keys",
    issuer="https://sts.windows.net/<ENTRATENANTID>/",
    audience="api://<APPUUID>",  # Replace with your actual app's URI
    required_scopes=["mcp.tools"]  # Adjust the required scopes as needed
)

# Mount MCP server to FastAPI
mcp = FastMCP("Joke Server", auth=auth)
# Create the ASGI app from your MCP server
mcp_app = mcp.http_app(path='/')
# Create a FastAPI app and mount the MCP server
app = FastAPI(lifespan=mcp_app.lifespan)
app.mount("/mcp", mcp_app)

# Trigger oauth-protected-resource external identity provider authentication flow
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    try:
        if request.url.path == "/mcp":
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Not authenticated"},
                    headers={"WWW-Authenticate": "Bearer error=\"invalid_request\", error_description=\"No access token was provided in this request\", resource_metadata=\"http://localhost:8000/.well-known/oauth-protected-resource\""},
                )

            #print(f"Authorization header: {auth_header}")

        response = await call_next(request)
        return response
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )
    
@app.get("/.well-known/oauth-protected-resource")
async def well_known_oauth_protected_resource():
    file_path = os.path.join(os.path.dirname(__file__), "oauth-protected-resource.json")
    return FileResponse(file_path, media_type="application/json")

# Define jokes tool
jokes = [
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "Why did the developer quit his job? He didn't get arrays!",
    "What's a programmer's favorite place? The foo bar!",
    "How many programmers does it take to change a light bulb? None, that's a hardware problem!",
    "What do you call a programmer from Finland? Nerdic!",
]
joke_iterator = cycle(jokes)

@mcp.tool()
def tell_joke() -> str:
    """Get a programming joke"""
    return next(joke_iterator)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

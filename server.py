# --- Entra ID (Azure AD) 3rd Party Authorization Code Flow Integration ---
import httpx
from fastapi.responses import RedirectResponse
import datetime
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.responses import JSONResponse, FileResponse
# Serve the OAuth Authorization Server metadata file
import os

from mcp.server.fastmcp import FastMCP
from itertools import cycle
# from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import time
# from typing import Optional

# Replace these with your actual Entra ID values
ENTRA_TENANT_ID = os.environ.get("ENTRA_TENANT_ID")
ENTRA_CLIENT_ID = os.environ.get("ENTRA_CLIENT_ID")
ENTRA_CLIENT_SECRET = os.environ.get("ENTRA_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8000/callback"  # Update as needed
SCOPE = "openid profile email"

ENTRA_AUTH_URL = f"https://login.microsoftonline.com/{ENTRA_TENANT_ID}/oauth2/v2.0/authorize"
ENTRA_TOKEN_URL = f"https://login.microsoftonline.com/{ENTRA_TENANT_ID}/oauth2/v2.0/token"


app = FastAPI()

# Create MCP server
mcp = FastMCP("Joke Server")

# Authentication middleware
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    try:
        if request.url.path == "/sse":
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Not authenticated"},
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            scheme, credentials = get_authorization_scheme_param(auth_header)
            if scheme.lower() != "bearer":
                # Here you would typically decode and validate the JWT token
                if credentials != None:
                    print(f"Received token: {credentials}")
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid authentication credentials"},
                    headers={"WWW-Authenticate": "Bearer"},
                )
    
        response = await call_next(request)
        return response
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )

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

# Add route for .well-known/oauth-authorization-server
# @app.get("/.well-known/oauth-authorization-server")
# async def get_oauth_metadata():
#     file_path = os.path.join(os.path.dirname(__file__), ".well-known", "oauth-authorization-server")
#     if not os.path.exists(file_path):
#         raise HTTPException(status_code=404, detail="Metadata file not found")
#     return FileResponse(file_path, media_type="application/json")


# RFC 7591-compliant client registration endpoint
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import uuid

class ClientRegistrationRequest(BaseModel):
    redirect_uris: List[str]
    client_name: Optional[str] = None
    grant_types: Optional[List[str]] = None
    response_types: Optional[List[str]] = None
    scope: Optional[str] = None
    token_endpoint_auth_method: Optional[str] = None
    jwks_uri: Optional[str] = None
    jwks: Optional[Dict] = None
    contacts: Optional[List[str]] = None
    logo_uri: Optional[str] = None
    client_uri: Optional[str] = None
    policy_uri: Optional[str] = None
    tos_uri: Optional[str] = None
    software_id: Optional[str] = None
    software_version: Optional[str] = None

class ClientRegistrationResponse(BaseModel):
    client_id: str
    client_id_issued_at: int
    client_secret_expires_at: int = 0  # 0 for public clients
    client_name: Optional[str] = None
    redirect_uris: List[str]
    token_endpoint_auth_method: str = "none"  # public client
    grant_types: Optional[List[str]] = None
    response_types: Optional[List[str]] = None
    scope: Optional[str] = None
    # Add other fields as needed

# In-memory client registry (for demo only)
registered_clients = {}

@app.post("/register", response_model=ClientRegistrationResponse, status_code=201)
async def register(registration: ClientRegistrationRequest):
    """Register the client with the MCP server (RFC 7591)"""
    now = int(time.time())
    client_id = str(uuid.uuid4())
    # For public clients, do not issue a secret
    client_data = {
        "client_id": client_id,
        "client_id_issued_at": now,
        "client_secret_expires_at": now+3600,
        "client_name": registration.client_name,
        "redirect_uris": registration.redirect_uris,
        "token_endpoint_auth_method": "none",
        "grant_types": registration.grant_types,
        "response_types": registration.response_types,
        "scope": registration.scope,
    }
    registered_clients[client_id] = client_data
    return client_data


# 1. Authorization endpoint: redirect user to Entra ID
@app.get("/authorize")
async def authorize(request: Request):
    state = str(uuid.uuid4())  # In production, store and validate state for CSRF protection
    client_id = request.query_params.get("client_id")
    url = (
        f"{ENTRA_AUTH_URL}"
        f"?client_id={ENTRA_CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_mode=query"
        f"&scope={SCOPE}"
        f"&state={state}"
    )
    response = RedirectResponse(url)
    if client_id:
        response.set_cookie(key="client_id", value=client_id, httponly=True, secure=False)
    return response

# 2. Callback endpoint: handle redirect and exchange code for tokens
@app.get("/callback")
async def callback(request: Request):
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    client_id = request.cookies.get("client_id")
    if not code:
        return JSONResponse(status_code=400, content={"error": "Missing code"})
    data = {
        "client_id": ENTRA_CLIENT_ID,
        "scope": SCOPE,
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
        "client_secret": ENTRA_CLIENT_SECRET,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(ENTRA_TOKEN_URL, data=data)
        token_response = resp.json()
    # Here you would associate the tokens with the user/session as needed
    if "error" in token_response:
        return JSONResponse(status_code=400, content={"error": token_response["error"]})
    
    if not client_id:
        return JSONResponse(status_code=400, content={"error": "cookie error"})

    if not client_id or client_id not in registered_clients:
        return JSONResponse(status_code=400, content={"error": "Invalid client_id"})

    if "redirect_uris" not in registered_clients[client_id]:
        return JSONResponse(status_code=400, content={"error": "Client not registered with redirect URIs"})
    
    registered_clients[client_id]["tokens"] = token_response
    registered_clients[client_id]["code"] = str(uuid.uuid4())
    response = RedirectResponse(registered_clients[client_id]["redirect_uris"][0] + f"?code={registered_clients[client_id]["code"]}&state={state}")
    response.delete_cookie("client_id")  # Clear the client_id cookie after use
    return response

# 3. Token endpoint: exchange code for token (OAuth2 spec)
@app.post("/token")
async def token(
    grant_type: str = Form(...),
    code: str = Form(...),
    redirect_uri: str = Form(...),
    client_id: str = Form(...),
    client_secret: str = Form(None)
):
    # Check if client_id exists
    client = registered_clients.get(client_id)
    if not client:
        return JSONResponse(status_code=400, content={"error": "invalid_client"})
    # Check if code matches
    if "code" not in client or client["code"] != code:
        return JSONResponse(status_code=400, content={"error": "invalid_grant"})
    # Check redirect_uri matches
    if redirect_uri not in client["redirect_uris"]:
        return JSONResponse(status_code=400, content={"error": "invalid_grant"})
    # Return the token stored for this client
    if "tokens" not in client:
        return JSONResponse(status_code=400, content={"error": "invalid_grant"})
    # Optionally, remove the code after use (one-time use)
    del client["code"]
    return JSONResponse(content=client["tokens"])


# Mount MCP server to FastAPI
app.mount("/", mcp.sse_app())

if __name__ == "__main__":
    #mcp.run(transport="sse")
    uvicorn.run(app, host="0.0.0.0", port=8000)

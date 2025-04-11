from fastapi import FastAPI, HTTPException, Request
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.responses import JSONResponse
from mcp.server.fastmcp import FastMCP
from itertools import cycle
# from fastapi.middleware.cors import CORSMiddleware
import uvicorn
# from typing import Optional

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
            if scheme.lower() != "bearer" or credentials != "valid_token":
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

# Mount MCP server to FastAPI
app.mount("/", mcp.sse_app())

if __name__ == "__main__":
    #mcp.run(transport="sse")
    uvicorn.run(app, host="0.0.0.0", port=8000)

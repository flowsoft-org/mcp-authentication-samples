# MCP Joke Server with Authentication

This is a sample implementation of a Model Context Protocol (MCP) server that serves programming jokes with token-based authentication using FastAPI.

## Setup

1. Open this folder in VS Code
2. When prompted, click "Reopen in Container" to use the devcontainer configuration
3. The container will automatically install all dependencies from requirements.txt

## Running the Server

```bash
python server.py
```

The server will start on http://localhost:8000

## Server Functionality

This MCP server provides a simple joke-telling capability. It cycles through a collection of programming-related jokes each time it's called. The server:

1. Implements a single MCP tool called `tell_joke`
2. Returns a different programming joke on each invocation
3. Requires authentication for accessing the SSE endpoint

## Authentication

The server implements a simple token-based authentication for the SSE endpoint (/sse). To make requests, you need to include a Bearer token in your HTTP headers.

For this demo, use the token: `valid_token`

Example curl request:
```bash
curl http://localhost:8000/sse \
  -H "Authorization: Bearer valid_token"
```

Any requests to the SSE endpoint without a valid token will receive a 401 Unauthorized response.

## VS Code Copilot Integration

This server can be used as a custom joke-telling agent for GitHub Copilot in VS Code. To use it:

1. Start the MCP server using `python server.py`
2. The VS Code settings are already configured in `.vscode/settings.json` to use this server
3. The server will respond to requests for jokes through the MCP protocol

### Supported Capabilities
- Joke telling via MCP tool
- Token-based authentication for SSE endpoint
- FastAPI-based HTTP server

## Security Note

This is a demonstration implementation. In a production environment, you should:
1. Use proper token validation
2. Store secrets securely
3. Implement proper token issuance and management
4. Use HTTPS
5. Add rate limiting and other security measures

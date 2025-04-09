# MCP Server with Authentication

This is a sample implementation of a Model Context Protocol (MCP) server with token-based authentication using FastAPI.

## Setup

1. Open this folder in VS Code
2. When prompted, click "Reopen in Container" to use the devcontainer configuration
3. The container will automatically install all dependencies from requirements.txt

## Running the Server

```bash
python server.py
```

The server will start on http://localhost:8000

## Authentication

The server implements a simple token-based authentication. To make requests, you need to include a Bearer token in your HTTP headers.

For this demo, use the token: `valid_token`

Example curl request:
```bash
curl -X POST http://localhost:8000/mcp/execute \
  -H "Authorization: Bearer valid_token" \
  -H "Content-Type: application/json" \
  -d '{"your": "mcp request here"}'
```

Any requests without a valid token will receive a 401 Unauthorized response.

## VS Code Copilot Integration

This server can be used as a custom agent for GitHub Copilot in VS Code. To use it:

1. Start the MCP server using `python server.py`
2. The VS Code settings are already configured in `.vscode/settings.json` to use this server
3. The server will handle agent-specific MCP messages and respond as GitHub Copilot

### Supported Agent Capabilities
- Semantic Search
- Function Calling
- File Editing
- Terminal Commands

## Security Note

This is a demonstration implementation. In a production environment, you should:
1. Use proper token validation
2. Store secrets securely
3. Implement proper token issuance and management
4. Use HTTPS
5. Add rate limiting and other security measures

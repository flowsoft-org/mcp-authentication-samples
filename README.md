# MCP Authentication Samples 🚀

This repository contains sample code for building Model Context Protocol (MCP) servers with OAuth2 authentication using FastAPI and FastMCP. The example implements a simple joke server that demonstrates how to protect MCP tools with Microsoft Entra ID (Azure AD) authentication.

## What's Included 📦

- **MCP Server with OAuth2 Authentication**: A FastAPI-based MCP server with bearer token validation
- **Joke Tool**: An example MCP tool that returns programming jokes
- **OAuth Protected Resource Discovery**: Implements RFC 9470 for OAuth 2.0 protected resource metadata
- **Dev Container Support**: Ready-to-use development container configuration for VS Code

## Prerequisites 📋

- Python 3.12 or higher
- Microsoft Entra ID (Azure AD) tenant and application registration
- VS Code (optional, but recommended for MCP integration)

## Quick Start 🚀

### 1. Setup Environment

**Option A: Using Dev Container (Recommended)**
1. Open this folder in VS Code
2. Click "Reopen in Container" when prompted
3. Dependencies will be installed automatically

**Option B: Local Setup**
1. Ensure Python 3.12+ is installed
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 2. Start the Server

```bash
python server.py
```

The server will start on http://localhost:8000

> **Note**: The server requires valid Azure AD configuration to work properly. See the configuration section below.

## Configure Microsoft Entra ID (Azure AD) 🔐

This sample demonstrates how to protect your MCP server using OAuth2 Bearer tokens from Microsoft Entra ID (Azure AD).

### Step 1: Register an Application in Azure AD 🛠️

1. **Navigate to Azure Portal**:
   - Go to [Azure Portal](https://portal.azure.com)
   - Navigate to "Microsoft Entra ID" (formerly Azure Active Directory)

2. **Create App Registration**:
   - Select "App registrations" → "New registration"
   - Enter a name (e.g., "MCP Joke Server")
   - Select supported account types (typically "Single tenant")
   - Click "Register"

3. **Note Your Application Details**:
   After registration, save these values:
   - **Tenant ID**: Found on the Overview page
   - **Application (client) ID**: Found on the Overview page (this is your `<APPUUID>`)

### Step 2: Expose an API 🔓

1. **Set Application ID URI**:
   - Go to "Expose an API" in your app registration
   - Click "Add" next to Application ID URI
   - Use the default format: `api://<APPUUID>` or customize it
   - Click "Save"

2. **Add a Scope**:
   - Click "Add a scope"
   - Scope name: `mcp.tools` (or your preferred scope name)
   - Admin consent display name: "Access MCP Tools"
   - Admin consent description: "Allows the application to access MCP tools"
   - State: Enabled
   - Click "Add scope"

3. **Note Your Scope**:
   - Your full scope will be: `api://<APPUUID>/mcp.tools`

### Step 3: Configure Client Application (Optional) 🔧

If you want to test with a specific client application:
1. Go to "Authentication" in your app registration
2. Add a platform (e.g., "Single-page application" or "Web")
3. Add redirect URIs as needed for your testing client

### Step 4: Update Configuration Files ✏️

#### Update `server.py`

Replace the placeholder values in the `BearerAuthProvider` configuration:

```python
auth = BearerAuthProvider(
    jwks_uri="https://login.microsoftonline.com/<ENTRATENANTID>/discovery/v2.0/keys",
    issuer="https://sts.windows.net/<ENTRATENANTID>/",
    algorithm="RS256",
    audience="api://<APPUUID>",
    required_scopes=["mcp.tools"]
)
```

Replace:
- `<ENTRATENANTID>`: Your Azure AD Tenant ID
- `<APPUUID>`: Your Application (client) ID
- `mcp.tools`: Your scope name (if you used a different scope name)

**Example with real values:**
```python
auth = BearerAuthProvider(
    jwks_uri="https://login.microsoftonline.com/12345678-1234-1234-1234-123456789abc/discovery/v2.0/keys",
    issuer="https://sts.windows.net/12345678-1234-1234-1234-123456789abc/",
    algorithm="RS256",
    audience="api://87654321-4321-4321-4321-cba987654321",
    required_scopes=["mcp.tools"]
)
```

#### Update `oauth-protected-resource.json`

This file implements [RFC 9470](https://datatracker.ietf.org/doc/html/rfc9470) for OAuth 2.0 protected resource metadata discovery. Update it with your values:

```json
{
  "resource": "http://localhost:8000/",
  "authorization_servers": [
    "https://login.microsoftonline.com/<ENTRATENANTID>/v2.0"
  ],
  "bearer_methods_supported": ["header"],
  "scopes_supported": [
    "api://<APPUUID>/mcp.tools"
  ]
}
```

Replace:
- `<ENTRATENANTID>`: Your Azure AD Tenant ID
- `<APPUUID>`: Your Application (client) ID
- `api://<APPUUID>/mcp.tools`: Your full scope identifier

**Example with real values:**
```json
{
  "resource": "http://localhost:8000/",
  "authorization_servers": [
    "https://login.microsoftonline.com/12345678-1234-1234-1234-123456789abc/v2.0"
  ],
  "bearer_methods_supported": ["header"],
  "scopes_supported": [
    "api://87654321-4321-4321-4321-cba987654321/mcp.tools"
  ]
}
```

## Using with GitHub Copilot 🤖

This MCP server can be used with GitHub Copilot in VS Code to provide authenticated tool access.

### Step 1: Configure MCP in VS Code

The repository includes a pre-configured `.vscode/mcp.json` file:

```json
{
    "servers": {
        "my-mcp-server-auth-jokes": {
            "type": "http",
            "url": "http://localhost:8000/mcp"
        }
    }
}
```

### Step 2: Start the Server

Ensure the MCP server is running:
```bash
python server.py
```

### Step 3: Use in GitHub Copilot

1. Open GitHub Copilot Chat in VS Code
2. The MCP server will be available with the configured tools
3. GitHub Copilot will handle the OAuth authentication flow automatically
4. You can now ask Copilot to use the joke tool: "Tell me a joke using the MCP server"

### Authentication Flow

When GitHub Copilot attempts to use the MCP server:
1. The server returns a 401 with OAuth metadata in the `WWW-Authenticate` header
2. GitHub Copilot reads the metadata from `/.well-known/oauth-protected-resource`
3. Copilot initiates the OAuth flow with Microsoft Entra ID
4. After authentication, Copilot includes the bearer token in subsequent requests

## Testing 🧪

### Test OAuth Discovery Endpoint

The server exposes OAuth 2.0 protected resource metadata:

```bash
curl http://localhost:8000/.well-known/oauth-protected-resource
```

This should return your OAuth configuration with authorization server and scope information.

### Test Without Authentication

Try accessing the MCP endpoint without a token:

```bash
curl -v http://localhost:8000/mcp
```

**Expected response:**
- Status: `401 Unauthorized`
- `WWW-Authenticate` header with OAuth metadata
- Response body: `{"detail": "Not authenticated"}`

### Test With Authentication

To test with a valid token, you need to obtain an access token from Azure AD:

#### Option 1: Using Azure CLI

```bash
# Login to Azure
az login

# Get an access token for your application
az account get-access-token --resource api://<APPUUID> --query accessToken -o tsv
```

Then use the token:

```bash
curl -H "Authorization: Bearer <YOUR_TOKEN>" http://localhost:8000/mcp
```

#### Option 2: Using OAuth 2.0 Client Credentials Flow

If you have configured a client application with client credentials:

```bash
# Get token using client credentials
TOKEN=$(curl -X POST "https://login.microsoftonline.com/<ENTRATENANTID>/oauth2/v2.0/token" \
  -d "client_id=<CLIENT_ID>" \
  -d "client_secret=<CLIENT_SECRET>" \
  -d "scope=api://<APPUUID>/.default" \
  -d "grant_type=client_credentials" | jq -r '.access_token')

# Use the token
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/mcp
```

### Testing the Joke Tool

Once authenticated (either through GitHub Copilot or direct API access), you can invoke the joke tool. The MCP protocol expects POST requests with the tool invocation payload.

**Example authenticated request:**
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "tell_joke"
    },
    "id": 1
  }'
```

**Expected response:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Why do programmers prefer dark mode? Because light attracts bugs!"
      }
    ]
  },
  "id": 1
}
```

## Project Structure 📁

```
.
├── .devcontainer/          # VS Code dev container configuration
│   └── devcontainer.json   # Dev container setup with Python 3.12
├── .vscode/                # VS Code workspace settings
│   └── mcp.json           # MCP server configuration for GitHub Copilot
├── server.py              # Main MCP server with OAuth authentication
├── oauth-protected-resource.json  # OAuth 2.0 resource metadata (RFC 9470)
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## How It Works 🔍

1. **FastAPI Server**: The application uses FastAPI as the web framework
2. **FastMCP Integration**: FastMCP provides the MCP protocol implementation
3. **Bearer Token Authentication**: The `BearerAuthProvider` validates JWT tokens from Azure AD
4. **OAuth Discovery**: The `/.well-known/oauth-protected-resource` endpoint provides metadata for OAuth clients
5. **Protected Endpoint**: The `/mcp` endpoint requires valid authentication
6. **Joke Tool**: A simple MCP tool that cycles through programming jokes

## Troubleshooting 🔧

### Common Issues

**Problem**: `401 Unauthorized` even with a valid token
- **Solution**: Verify that the token's audience (`aud` claim) matches the `audience` in `server.py`
- Check that the token's issuer (`iss` claim) matches the `issuer` in `server.py`
- Ensure the token includes the required scope (`mcp.tools`)

**Problem**: Can't obtain a token using Azure CLI
- **Solution**: Make sure you're logged in with an account that has access to the application
- Try `az login --tenant <ENTRATENANTID>` to specify the tenant explicitly

**Problem**: GitHub Copilot can't authenticate
- **Solution**: Ensure the server is running and accessible at `http://localhost:8000`
- Check that `oauth-protected-resource.json` is correctly configured
- Restart VS Code after updating `mcp.json`

**Problem**: Token validation fails with JWKS errors
- **Solution**: Verify the `jwks_uri` is correct and accessible
- Ensure your Azure AD tenant ID is correct in the URI

## Additional Resources 📚

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Microsoft Entra ID Documentation](https://learn.microsoft.com/en-us/entra/identity/)
- [RFC 9470 - OAuth 2.0 Protected Resource Metadata](https://datatracker.ietf.org/doc/html/rfc9470)

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

## License 📜

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

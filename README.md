# MCP Authentication Samples 🚀

This repository contains sample code for building Model Context Protocol (MCP) servers with authentication using FastAPI and FastMCP.

## Running the Server 🖥️

1. Open this folder in VS Code
2. (If using devcontainer) Click "Reopen in Container" if prompted
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the server:
   ```bash
   python server.py
   ```

The server will start on http://localhost:8000

## Authentication with Microsoft Entra ID (Azure AD) 🔐

This sample demonstrates how to protect your MCP server using OAuth2 Bearer tokens from Microsoft Entra ID (Azure AD).

### Required Entra ID Application Setup 🛠️

1. **Register an Application** in Microsoft Entra ID (Azure AD) via the Azure Portal.
2. **Expose an API**:
   - Go to "Expose an API" in your app registration.
   - Set the Application ID URI (e.g., `api://<APPUUID>`).
   - Add a scope (e.g., `mcp.tools`).
3. **Configure Authentication**:
   - Add a redirect URI if needed for your client.
4. **Get the following values** for your app:
   - Tenant ID
   - Application (client) ID
   - Application ID URI
   - Scope name

### Update Your Code and Resource Metadata ✏️

- **Update `BearerAuthProvider` in `server.py`:**
  - Replace `<ENTRATENANTID>` with your Entra tenant ID.
  - Replace `<APPUUID>` with your Application (client) ID or Application ID URI.
  - Set the correct `jwks_uri`, `issuer`, `audience`, and `required_scopes`.

  Example:
  ```python
  auth = BearerAuthProvider(
      jwks_uri="https://login.microsoftonline.com/<ENTRATENANTID>/discovery/v2.0/keys",
      issuer="https://sts.windows.net/<ENTRATENANTID>/",
      algorithm="RS256",
      audience="api://<APPUUID>",
      required_scopes=["mcp.tools"]
  )
  ```

- **Update `oauth-protected-resource.json`:**
  - Ensure this file matches your application's metadata, including resource ID, scopes, and issuer.

### Example: oauth-protected-resource.json 📄

```json
{
  "resource": "api://<APPUUID>",
  "issuer": "https://sts.windows.net/<ENTRATENANTID>/",
  "scopes": ["mcp.tools"]
}
```

Replace placeholders with your actual values.

## GitHub Copilot Agent Mode 🤖

This MCP server can also be used in GitHub Copilot Agent mode in VS Code. To enable this:

1. Ensure the server is running.
2. Use the `mcp.json` file to configure the MCP server for GitHub Copilot.
3. Start the server from the `mcp.json` configuration.

## Testing 🧪

You can test the protected endpoint using curl:

```
curl -H "Authorization: Bearer <token>" http://localhost:8000/mcp
```

If no or an invalid token is provided, you will receive a 401 Unauthorized response.

## License 📜

See [LICENSE](LICENSE).

# FastMCP Setup Guide

This guide explains how to set up and use the FastMCP 2.0 integration with your LMS API.

## What is FastMCP?

FastMCP is a Python library that makes it easy to build MCP (Model Context Protocol) servers. MCP is a standardized protocol that allows LLMs to interact with external tools and data sources. It's often described as "the USB-C port for AI".

## Installation

1. **Install FastMCP dependency**:
   ```bash
   pip install fastmcp==2.0.0
   ```

2. **Install all dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation**:
   ```bash
   fastmcp version
   ```

## Transport Options

FastMCP 2.0 supports two transport protocols:

### 🎯 STDIO Transport (Default - Recommended)
- **Best for**: Claude Desktop, process-based MCP clients
- **Security**: Most secure - no network exposure  
- **Performance**: Direct process communication
- **Setup**: Minimal configuration required

### 🌐 SSE Transport (Server-Sent Events)
- **Best for**: Web browsers, real-time streaming applications
- **Usage**: Browser-based MCP clients using EventSource API
- **Network**: Requires HTTP server on specified port
- **Real-time**: Supports streaming updates

## Running the MCP Server

### Default (STDIO Transport):
```bash
# Simple startup
python run_mcp.py

# Or directly
python app/mcp_server.py
```

### SSE Transport:
```bash
# Default SSE (localhost:8001)
python app/mcp_server.py sse

# Custom host and port
python app/mcp_server.py sse 0.0.0.0 8002

# Custom host only
python app/mcp_server.py sse 192.168.1.100
```

### Server Output:
```bash
$ python run_mcp.py
Starting LMS MCP Server with STDIO transport...
Running with STDIO transport (best for Claude Desktop)
# Server ready for connections

$ python app/mcp_server.py sse
Starting LMS MCP Server with SSE transport...
Running with SSE transport on localhost:8001
SSE endpoint: http://localhost:8001/sse
# Server listening on HTTP
```

## Available Tools

### 🔧 Tools (Functions)
- `list_answer_types()`: Get all answer types with French translations
- `get_answer_type(answer_type_id: int)`: Get specific answer type details  
- `search_answer_types(keyword: str, is_valid: bool)`: Search and filter answer types

### 📚 Resources (Data)
- `lms_database_schema()`: Get comprehensive database schema documentation

### 💡 Prompts (Templates)
- `explain_answer_type(answer_type_id: int)`: Generate educational explanations

## Claude Desktop Integration

### 1. Locate Configuration File
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### 2. Add LMS MCP Server
```json
{
  "mcpServers": {
    "lms-api": {
      "command": "python",
      "args": ["run_mcp.py"],
      "cwd": "C:\\full\\path\\to\\bonus\\api",
      "env": {
        "MYSQL_HOST": "localhost",
        "MYSQL_USER": "your_mysql_user",
        "MYSQL_DATABASE": "lms",
        "MYSQL_PASSWORD": "your_mysql_password",
        "REDIS_HOST": "localhost",
        "REDIS_PORT": "6379"
      }
    }
  }
}
```

### 3. Alternative Configuration (Unix/macOS)
```json
{
  "mcpServers": {
    "lms-api": {
      "command": "python",
      "args": ["run_mcp.py"],
      "cwd": "/full/path/to/bonus/api",
      "env": {
        "MYSQL_HOST": "localhost",
        "MYSQL_USER": "lms",
        "MYSQL_DATABASE": "lms",
        "MYSQL_PASSWORD": "password",
        "REDIS_HOST": "localhost",
        "REDIS_PORT": "6379"
      }
    }
  }
}
```

### 4. Restart Claude Desktop

### 5. Test Connection
Ask Claude:
```
Can you list all the answer types available in the LMS system?
```

## Environment Variables

Create a `.env` file in the `bonus/api` directory:

```env
# Database Configuration
MYSQL_HOST=localhost
MYSQL_USER=lms
MYSQL_DATABASE=lms
MYSQL_PASSWORD=your_password

# Redis Configuration  
REDIS_HOST=localhost
REDIS_PORT=6379

# API Configuration
JWT_SECRET_KEY=your-secret-key
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=your-admin-password
```

## Testing the MCP Server

### Manual Testing

1. **Test STDIO transport**:
   ```bash
   python run_mcp.py
   # Server starts and waits for STDIO connections
   ```

2. **Test SSE transport**:
   ```bash
   python app/mcp_server.py sse
   # Visit http://localhost:8001/sse in browser dev tools
   ```

### Using with Claude Desktop

Once configured, you can interact with the LMS system:

1. **List all answer types**:
   ```
   Show me all answer types in the LMS system with their French translations
   ```

2. **Get specific answer type**:
   ```
   Get details for answer type with ID 1, including its French translation
   ```

3. **Search answer types**:
   ```
   Search for answer types containing the keyword "choice" that are currently valid
   ```

4. **Get database schema**:
   ```
   Show me the database schema for answer types including relationships
   ```

5. **Educational explanation**:
   ```
   Explain answer type ID 2 in detail for educational purposes
   ```

## Troubleshooting

### Common Issues

1. **Import Error: `fastmcp` not found**:
   ```bash
   # Solution: Install FastMCP
   pip install fastmcp==2.0.0
   
   # Verify installation
   python -c "import fastmcp; print(fastmcp.__version__)"
   ```

2. **Database Connection Error**:
   ```bash
   # Check MySQL service
   # Windows
   net start mysql
   
   # Linux/macOS  
   sudo systemctl start mysql
   # or
   brew services start mysql
   
   # Verify connection
   mysql -u lms -p -h localhost lms
   ```

3. **Environment Variables Not Loaded**:
   ```bash
   # Verify .env file location
   ls -la bonus/api/.env
   
   # Test environment loading
   python -c "from app.core.config import settings; print(settings.MYSQL_HOST)"
   ```

4. **MCP Server Not Starting**:
   ```bash
   # Check Python path
   python -c "import sys; print(sys.path)"
   
   # Verify all dependencies
   pip list | grep -E "(fastmcp|aiomysql|fastapi)"
   ```

5. **Port Already in Use (SSE)**:
   ```bash
   # Find process using port
   netstat -ano | findstr :8001
   
   # Use different port
   python app/mcp_server.py sse localhost 8002
   ```

### Debug Mode

Run with detailed logging:
```bash
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from app.mcp_server import run_mcp_server
run_mcp_server('stdio')
"
```

### Testing Database Connection
```bash
python -c "
import asyncio
from app.db.session import get_db_connection

async def test():
    try:
        db = await get_db_connection()
        print('✅ Database connection successful')
        await db.ensure_closed()
    except Exception as e:
        print(f'❌ Database error: {e}')

asyncio.run(test())
"
```

## Advanced Configuration

### Multiple Transport Support

Run both transports simultaneously:

```bash
# Terminal 1: STDIO
python run_mcp.py

# Terminal 2: SSE  
python app/mcp_server.py sse localhost 8002
```

### Custom Environment Configuration

```bash
# Development
MYSQL_HOST=localhost python run_mcp.py

# Production
MYSQL_HOST=prod-db.example.com python run_mcp.py
```

### Docker Integration

```dockerfile
# Add to your Dockerfile
RUN pip install fastmcp==2.0.0

# Run MCP server
CMD ["python", "run_mcp.py"]
```

## Extending the MCP Server

### Adding New Tools

1. **Add a new tool function** in `app/mcp_server.py`:
   ```python
   @mcp.tool()
   async def create_answer_type(title: str, description: str) -> Dict[str, Any]:
       """
       Create a new answer type in the LMS system.
       
       Args:
           title: The title of the answer type
           description: Description of the answer type
           
       Returns:
           Dictionary with creation result
       """
       try:
           db = await get_db_connection()
           # Implementation here
           return {"success": True, "id": new_id}
       except Exception as e:
           return {"error": f"Failed to create: {str(e)}"}
   ```

2. **Add a new resource**:
   ```python
   @mcp.resource(uri="lms://users/schema")
   async def lms_users_schema() -> str:
       """Get user table schema information."""
       return "User table schema documentation..."
   ```

3. **Add a new prompt template**:
   ```python
   @mcp.prompt()
   async def compare_answer_types(type1_id: int, type2_id: int) -> str:
       """Compare two answer types for educational analysis."""
       # Implementation here
       return f"Comparison between types {type1_id} and {type2_id}"
   ```

## Best Practices

### Security
1. **Never expose sensitive operations** through MCP tools
2. **Validate all input parameters** before processing
3. **Use environment variables** for sensitive configuration
4. **Implement proper error handling** to avoid information leakage

### Performance
1. **Use async operations** for all database calls
2. **Implement connection pooling** for database operations
3. **Cache frequently accessed data** when appropriate
4. **Limit result set sizes** for large datasets

### Development
1. **Use proper type hints** for all function parameters and returns
2. **Provide clear docstrings** for all tools, resources, and prompts
3. **Test tools individually** before deploying
4. **Monitor logs** for errors and performance issues

### Error Handling
```python
@mcp.tool()
async def safe_tool_example(param: str) -> Dict[str, Any]:
    """Example of proper error handling in MCP tools."""
    try:
        # Validate input
        if not param or len(param) < 1:
            return {"error": "Parameter must be non-empty string"}
        
        # Process request
        result = await some_async_operation(param)
        return {"success": True, "data": result}
        
    except ValueError as e:
        return {"error": f"Invalid input: {str(e)}"}
    except Exception as e:
        # Log the full error for debugging
        logger.error(f"Unexpected error in safe_tool_example: {e}")
        return {"error": "An unexpected error occurred"}
```

## Transport Decision Guide

| Use Case | Recommended Transport | Reason |
|----------|----------------------|---------|
| Claude Desktop | STDIO | Native support, secure |
| Web Development | SSE | Browser compatibility |
| CI/CD Integration | STDIO | Process-based, reliable |
| Real-time Apps | SSE | Streaming capabilities |
| Production | STDIO | More secure, stable |
| Development/Testing | Either | Based on client needs |

## Additional Resources

- **FastMCP Documentation**: [https://gofastmcp.com/](https://gofastmcp.com/)
- **Model Context Protocol**: [https://modelcontextprotocol.io/](https://modelcontextprotocol.io/)
- **Claude Desktop MCP Guide**: [https://docs.anthropic.com/claude/docs/mcp](https://docs.anthropic.com/claude/docs/mcp)
- **FastMCP GitHub**: [https://github.com/jlowin/fastmcp](https://github.com/jlowin/fastmcp) 
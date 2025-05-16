# LMS V3 API

A FastAPI-based REST API for the LMS V3 platform.

## Project Structure

```
app/
├── api/                   # API layer - all HTTP endpoints
│   └── v1/                # API version 1
│       ├── deps/          # Dependencies (auth, db, etc.)
│       │   └── auth.py    # Authentication dependencies
│       └── endpoints/     # Route handlers
│           ├── public/    # Public endpoints (no auth required)
│           │   └── formations.py
│           └── private/   # Private endpoints (auth required)
│               └── sessions.py
│               └── formations.py
│               └── modules.py
├── core/                  # Core application logic
│   ├── config.py          # App configuration & settings
│   └── security.py        # Security utilities (JWT, password hashing)
├── db/                    # Database layer
│   └── session.py         # Database connection & session management
├── models/                # Data models & schemas
│   └── models.py          # Pydantic models for request/response
└── main.py                # Application entry point

tests/                     # Test suite
├── conftest.py            # pytest fixtures & configuration
├── api/                   # API tests
│   └── v1/
│       ├── test_formations.py
│       └── test_auth.py
├── core/                 # Core functionality tests
│   └── test_security.py
├── db/                   # Database tests
│   └── test_session.py
└── integration/          # End-to-end tests
    └── test_api.py
```

## Directory Structure Explained

### `/app/api`
- Contains all HTTP endpoints and API-related code
- Organized by version (v1) for future versioning support
- Separated into public and private endpoints
- Dependencies are shared across endpoints

### `/app/core`
- Core application logic and configuration
- Contains settings management and security utilities
- No direct HTTP or database dependencies

### `/app/db`
- Database connection and session management
- Handles database pooling and connection lifecycle
- Contains database utilities and helpers

### `/app/models`
- Pydantic models for request/response validation
- Data transfer objects (DTOs)
- Shared data structures

### `/tests`
- Comprehensive test suite
- Organized to mirror the app structure
- Includes fixtures, unit tests, and integration tests

## Setup

1. Create a `.env` file in the root directory with the following variables:

```env
JWT_SECRET_KEY=your-secret-key
MYSQL_HOST=localhost
MYSQL_USER=lms
MYSQL_DATABASE=lms
MYSQL_PASSWORD=password
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=your-admin-password
REDIS_HOST=localhost
REDIS_PORT=6379
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate # Linux/MacOS
.\venv\Scripts\activate # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the application:

```bash
uvicorn app.main:app --reload
```

## Test

```bash
pytest app/tests/api/v1/test_auth.py -v
```

## API Documentation

Once the application is running, you can access:
- Swagger UI documentation at: http://localhost:8000/docs
- ReDoc documentation at: http://localhost:8000/redoc

## Authentication

The API uses JWT token-based authentication. To get a token:

1. Make a POST request to `/api/v1/auth/token` with:
```json
{
    "username": "admin@example.com",
    "password": "your-admin-password"
}
```

2. Use the returned token in the Authorization header:
```
Authorization: Bearer <your-token>
```

## API Endpoints

### Authentication
- `POST /token` - Get JWT token

### Get Token
```bash 
curl -X POST "http://localhost:8000/api/v1/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=your@email.com&password=yourpassword"
```

### Get Profile
```bash
curl "http://localhost:8000/api/v1/profile/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Models

### User
```python
{
    "id": int,
    "email": str,
    "firstname": str,
    "lastname": str,
    "valid": bool,
}
```

## MySQL Request Guide

### Best Practices

1. **Use Column Names Instead of Indices**
```python
# Good
row_dict = dict(zip(column_names, row))
user_id = row_dict["id"]
username = row_dict["username"]

# Bad
user_id = row[0]
username = row[1]
```

2. **Proper JOIN Syntax**
```sql
-- Good: Explicit JOIN with clear aliases
SELECT e.id, e.title, c.title as country_title
FROM event e
LEFT JOIN country c ON e.country_id = c.id

-- Bad: Implicit join
SELECT event.id, event.title, country.title
FROM event, country
WHERE event.country_id = country.id
```

3. **Column Aliasing for Clarity**
```sql
-- Good: Clear column aliases for joined tables
SELECT 
    e.id,
    e.title as event_title,
    c.id as country_id,
    c.title as country_title

-- Bad: Ambiguous column names
SELECT id, title, country.id, country.title
```

4. **Async/Await Usage**
```python
# Good
async with db.cursor() as cursor:
    await cursor.execute(
        "SELECT id, title FROM event WHERE id = %s",
        (event_id,)
    )
    row = await cursor.fetchone()

# Bad
cursor = db.cursor()
cursor.execute("SELECT id, title FROM event")
row = cursor.fetchone()
```

5. **Parameter Binding for Security**
```python
# Good: Using parameterized queries
await cursor.execute(
    "SELECT * FROM event WHERE id = %s AND valid = %s",
    (event_id, True)
)

# Bad: String formatting (SQL injection risk)
await cursor.execute(
    f"SELECT * FROM event WHERE id = {event_id}"
)
```

6. **Error Handling**
```python
try:
    async with db.cursor() as cursor:
        await cursor.execute(query, params)
        result = await cursor.fetchall()
except Exception as e:
    logger.error(f"Database error: {str(e)}")
    raise HTTPException(status_code=500, detail="Database error")
```

### Common Query Patterns

1. **Pagination**
```sql
SELECT *
FROM table_name
LIMIT %s OFFSET %s
```

2. **Joins with Multiple Conditions**
```sql
SELECT e.*, c.title as category_title
FROM event e
LEFT JOIN category c ON e.category_id = c.id
WHERE e.valid = TRUE
  AND e.date >= CURRENT_DATE
ORDER BY e.date DESC
```

3. **Aggregation**
```sql
SELECT 
    country_id,
    COUNT(*) as event_count,
    MAX(dateEvent) as latest_event
FROM event
GROUP BY country_id
HAVING COUNT(*) > 1
```

4. **Subqueries**
```sql
SELECT *
FROM event
WHERE country_id IN (
    SELECT id 
    FROM country 
    WHERE active = TRUE
)
```

## Error Handling

- 401 - Unauthorized (invalid/missing token)
- 404 - Resource not found
- 500 - Server/database error

## Development

Built with:
- FastAPI
- MySQL
- JWT Authentication
- Python 3.8+

## Security Features

- JWT token authentication
- Password hashing
- SQL injection protection
- Input validation via Pydantic models
- Database connection pooling
- Error handling and logging

## Testing

To run tests:

```bash
pytest
```

To run with coverage:

```bash
pytest --cov=app
```

To run integration tests:

```bash
pytest tests/integration/test_api.py
```

To run specific tests:

```bash
pytest app/tests/api/v1/test_formations.py -v
```

## Development Guidelines

### Code Organization
- Keep related code together (e.g., all department-related code in one place)
- Use clear, descriptive file names (e.g., `events.py` instead of `dept.py`)
- Follow the established directory structure for new features

### API Development
- Place new endpoints in appropriate `public/` or `private/` folders
- Use FastAPI's dependency injection for shared logic
- Always include proper request/response models
- Document endpoints with clear docstrings

### Database Operations
- Use async database operations
- Keep database queries in dedicated service files
- Use connection pooling for better performance
- Handle database errors gracefully

### Testing
- Write tests for all new features
- Place tests in corresponding test directories
- Use pytest fixtures for common setup
- Include both unit and integration tests

### Security
- Never store sensitive data in code
- Use environment variables for secrets
- Validate all user input
- Implement proper authentication checks

### Code Style
- Follow PEP 8 guidelines
- Use type hints for all functions
- Write clear, concise docstrings
- Keep functions focused and small

### Performance
- Use async/await for I/O operations
- Implement caching where appropriate
- Optimize database queries
- Monitor response times

### Error Handling
- Use FastAPI's HTTPException for API errors
- Log errors with proper context
- Return meaningful error messages
- Handle edge cases explicitly

## Optimizes performance in FastAPI APIs by using async functions, caching, and other techniques.

- Minimize blocking I/O operations using async functions.
- Implement caching strategies for frequently accessed data using Redis or in-memory stores.
- Use lazy loading techniques for large datasets and API responses.
- Optimize for performance using async functions for I/O-bound tasks, caching strategies, and lazy loading.
- Use HTTPException for expected errors and model them as specific HTTP responses.
- Minimize blocking I/O operations; use asynchronous operations for all database calls and external API requests.
- Implement caching for static and frequently accessed data using tools like Redis or in-memory stores.
- Optimize data serialization and deserialization with Pydantic.
- Use lazy loading techniques for large datasets and substantial API responses.

## Component usage

- Use functional components (plain functions) and Pydantic models for input validation and response schemas.
- Use declarative route definitions with clear return type annotation.
- Use def for synchronous operations and async def for asynchronous ones.
- Minimize @app.on_event("startup") and @app.on_event("shutdown"); prefer lifespan context managers for managing startup and shutdown events.
- Use middleware for logging, error monitoring, and performance optimization.

## Conventions specific to this project

- Follow RESTful API design principles.
- Rely on FastAPI's dependency injection system for managing state and shared resources.
- Use SQLAlchemy 2.0 for ORM features, if applicable.
- Ensure CORS is properly configured for local development.
- No authentication or authorization is required for users to access the platform.

## Best practices

- Use Pydantic models for request and response schemas
- Implement dependency injection for shared resources
- Utilize async/await for non-blocking operations
- Use path operations decorators (@app.get, @app.post, etc.)
- Implement proper error handling with HTTPException
- Use FastAPI's built-in OpenAPI and JSON Schema support

## Specifies the preferred asynchronous database libraries and interaction patterns

- Async database libraries like asyncpg or aiomysql.
- SQLAlchemy 2.0 (if using ORM features).
- Minimize blocking I/O operations; use asynchronous operations for all database calls.

## Defines how errors should be handled and logged

- Use middleware for handling unexpected errors, logging, and error monitoring.
- Prioritize error handling and edge cases.
- Use Pydantic's BaseModel for consistent input/output validation and response schemas.

## Guidelines for defining Pydantic models within the models directory

- Use Pydantic models for request and response schemas
- Define data types using Pydantic fields
- Implement validation logic using Pydantic validators
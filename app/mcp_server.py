"""
MCP Server for LMS API

This module creates an MCP server that exposes the LMS API endpoints as tools
that can be used by LLMs for interacting with the learning management system.

Supports multiple transport options:
- STDIO (default): For process-based clients like Claude Desktop
- SSE: For real-time streaming applications
"""

import asyncio
import json
import os
import sys
from typing import List, Dict, Any, Optional, Literal
from fastmcp import FastMCP
from app.core.config import settings
from app.db.session import get_db_connection
from app.models.lov.answer_type import AnswerType, AnswerTypeCreate
from datetime import datetime

# Initialize MCP server
mcp = FastMCP("LMS API Server 🎓")

@mcp.tool()
async def list_answer_types() -> List[Dict[str, Any]]:
    """
    List all answer types available in the LMS system.
    
    Returns:
        List of answer types with their details including translations.
    """
    try:
        db = await get_db_connection()
        async with db.cursor() as cursor:
            # Get all answer types
            await cursor.execute("""
                SELECT
                    at.id,
                    cu.id as create_user_id, cu.firstname as create_user_firstname, cu.lastname as create_user_lastname,
                    uu.id as update_user_id, uu.firstname as update_user_firstname, uu.lastname as update_user_lastname,
                    at.title, at.description, at.keywords, at.sort, at.revision, at.create_date, at.update_date, at.is_valid, at.conditional
                FROM answer_type at
                LEFT JOIN fos_user cu ON at.create_user_id = cu.id
                LEFT JOIN fos_user uu ON at.update_user_id = uu.id
            """)
            rows = await cursor.fetchall()
            
            # Get French translations separately
            if rows:
                answer_type_ids = [str(row[0]) for row in rows]
                placeholders = ','.join(['%s'] * len(answer_type_ids))
                await cursor.execute(f"""
                    SELECT foreign_key, content 
                    FROM ext_translations 
                    WHERE object_class LIKE %s
                    AND field = %s
                    AND locale = %s
                    AND foreign_key IN ({placeholders})
                """, ('%AnswerType%', 'title', 'fr', *answer_type_ids))
                translations = {str(row[0]): row[1] for row in await cursor.fetchall()}
            else:
                translations = {}
        
        result = []
        for row in rows:
            result.append({
                "id": row[0],
                "create_user": {
                    "user_id": row[1],
                    "firstname": row[2],
                    "lastname": row[3]
                } if row[1] else None,
                "update_user": {
                    "user_id": row[4],
                    "firstname": row[5],
                    "lastname": row[6]
                } if row[4] else None,
                "title": row[7],
                "title_fr": translations.get(str(row[0])),
                "description": row[8],
                "keywords": row[9],
                "sort": row[10],
                "revision": row[11],
                "create_date": row[12].isoformat() if row[12] else None,
                "update_date": row[13].isoformat() if row[13] else None,
                "is_valid": bool(row[14]),
                "conditional": row[15]
            })
        
        return result
        
    except Exception as e:
        return [{"error": f"Failed to retrieve answer types: {str(e)}"}]

@mcp.tool()
async def get_answer_type(answer_type_id: int) -> Dict[str, Any]:
    """
    Get a specific answer type by ID.
    
    Args:
        answer_type_id: The ID of the answer type to retrieve
        
    Returns:
        Dictionary containing the answer type details.
    """
    try:
        db = await get_db_connection()
        async with db.cursor() as cursor:
            # Get the answer type
            await cursor.execute("""
                SELECT
                    at.id,
                    cu.id as create_user_id, cu.firstname as create_user_firstname, cu.lastname as create_user_lastname,
                    uu.id as update_user_id, uu.firstname as update_user_firstname, uu.lastname as update_user_lastname,
                    at.title, at.description, at.keywords, at.sort, at.revision, at.create_date, at.update_date, at.is_valid, at.conditional
                FROM answer_type at
                LEFT JOIN fos_user cu ON at.create_user_id = cu.id
                LEFT JOIN fos_user uu ON at.update_user_id = uu.id
                WHERE at.id = %s
            """, (answer_type_id,))
            row = await cursor.fetchone()
            
            if not row:
                return {"error": "Answer type not found"}
            
            # Get French translation separately
            await cursor.execute("""
                SELECT content 
                FROM ext_translations 
                WHERE object_class LIKE %s
                AND field = %s
                AND locale = %s
                AND foreign_key = %s
            """, ('%AnswerType%', 'title', 'fr', str(answer_type_id)))
            translation_row = await cursor.fetchone()
            title_fr = translation_row[0] if translation_row else None
            
        return {
            "id": row[0],
            "create_user": {
                "user_id": row[1],
                "firstname": row[2],
                "lastname": row[3]
            } if row[1] else None,
            "update_user": {
                "user_id": row[4],
                "firstname": row[5],
                "lastname": row[6]
            } if row[4] else None,
            "title": row[7],
            "title_fr": title_fr,
            "description": row[8],
            "keywords": row[9],
            "sort": row[10],
            "revision": row[11],
            "create_date": row[12].isoformat() if row[12] else None,
            "update_date": row[13].isoformat() if row[13] else None,
            "is_valid": bool(row[14]),
            "conditional": row[15]
        }
        
    except Exception as e:
        return {"error": f"Failed to retrieve answer type: {str(e)}"}

@mcp.tool()
async def search_answer_types(keyword: Optional[str] = None, is_valid: Optional[bool] = None) -> List[Dict[str, Any]]:
    """
    Search answer types based on criteria.
    
    Args:
        keyword: Optional keyword to search in title, description, or keywords
        is_valid: Optional filter for valid/invalid answer types
        
    Returns:
        List of matching answer types.
    """
    try:
        db = await get_db_connection()
        async with db.cursor() as cursor:
            # Build dynamic query
            where_conditions = []
            params = []
            
            if keyword:
                where_conditions.append("(at.title LIKE %s OR at.description LIKE %s OR at.keywords LIKE %s)")
                keyword_param = f"%{keyword}%"
                params.extend([keyword_param, keyword_param, keyword_param])
                
            if is_valid is not None:
                where_conditions.append("at.is_valid = %s")
                params.append(str(1 if is_valid else 0))  # Convert bool to string for MySQL
            
            where_clause = ""
            if where_conditions:
                where_clause = "WHERE " + " AND ".join(where_conditions)
            
            query = f"""
                SELECT
                    at.id,
                    cu.id as create_user_id, cu.firstname as create_user_firstname, cu.lastname as create_user_lastname,
                    uu.id as update_user_id, uu.firstname as update_user_firstname, uu.lastname as update_user_lastname,
                    at.title, at.description, at.keywords, at.sort, at.revision, at.create_date, at.update_date, at.is_valid, at.conditional
                FROM answer_type at
                LEFT JOIN fos_user cu ON at.create_user_id = cu.id
                LEFT JOIN fos_user uu ON at.update_user_id = uu.id
                {where_clause}
                ORDER BY at.sort, at.title
            """
            
            await cursor.execute(query, params)
            rows = await cursor.fetchall()
            
            # Get French translations
            if rows:
                answer_type_ids = [str(row[0]) for row in rows]
                placeholders = ','.join(['%s'] * len(answer_type_ids))
                await cursor.execute(f"""
                    SELECT foreign_key, content 
                    FROM ext_translations 
                    WHERE object_class LIKE %s
                    AND field = %s
                    AND locale = %s
                    AND foreign_key IN ({placeholders})
                """, ('%AnswerType%', 'title', 'fr', *answer_type_ids))
                translations = {str(row[0]): row[1] for row in await cursor.fetchall()}
            else:
                translations = {}
        
        result = []
        for row in rows:
            result.append({
                "id": row[0],
                "create_user": {
                    "user_id": row[1],
                    "firstname": row[2],
                    "lastname": row[3]
                } if row[1] else None,
                "update_user": {
                    "user_id": row[4],
                    "firstname": row[5],
                    "lastname": row[6]
                } if row[4] else None,
                "title": row[7],
                "title_fr": translations.get(str(row[0])),
                "description": row[8],
                "keywords": row[9],
                "sort": row[10],
                "revision": row[11],
                "create_date": row[12].isoformat() if row[12] else None,
                "update_date": row[13].isoformat() if row[13] else None,
                "is_valid": bool(row[14]),
                "conditional": row[15]
            })
        
        return result
        
    except Exception as e:
        return [{"error": f"Failed to search answer types: {str(e)}"}]

@mcp.resource(uri="lms://database/schema")
async def lms_database_schema() -> str:
    """
    Get information about the LMS database schema for answer types.
    
    Returns:
        String describing the database schema and relationships.
    """
    return """
    LMS Database Schema - Answer Types:
    
    Main Tables:
    - answer_type: Stores answer type definitions
      - id (INT): Primary key
      - title (VARCHAR): Answer type title in default language
      - description (TEXT): Description of the answer type
      - keywords (VARCHAR): Keywords for searching
      - sort (INT): Sort order
      - revision (INT): Version number
      - is_valid (BOOLEAN): Active/inactive status
      - conditional (VARCHAR): URL-friendly slug
      - create_user_id (INT): Foreign key to fos_user
      - update_user_id (INT): Foreign key to fos_user
      - create_date (DATETIME): Creation timestamp
      - update_date (DATETIME): Last update timestamp
    
    - ext_translations: Stores multilingual translations
      - object_class (VARCHAR): Entity class name
      - foreign_key (VARCHAR): ID of the translated entity
      - field (VARCHAR): Field being translated
      - locale (VARCHAR): Language code (e.g., 'fr', 'en')
      - content (TEXT): Translated content
    
    - fos_user: User information
      - id (INT): Primary key
      - firstname (VARCHAR): User's first name
      - lastname (VARCHAR): User's last name
    
    Relationships:
    - answer_type.create_user_id -> fos_user.id
    - answer_type.update_user_id -> fos_user.id
    - ext_translations links to answer_type via object_class and foreign_key
    """

@mcp.prompt()
async def explain_answer_type(answer_type_id: int) -> str:
    """
    Generate a detailed explanation of an answer type for educational purposes.
    
    Args:
        answer_type_id: The ID of the answer type to explain
    """
    answer_type = await get_answer_type(answer_type_id)
    
    if "error" in answer_type:
        return f"Could not find answer type with ID {answer_type_id}"
    
    explanation = f"""
    Answer Type: {answer_type['title']}
    {'French Title: ' + answer_type['title_fr'] if answer_type['title_fr'] else ''}
    
    Description: {answer_type['description'] or 'No description available'}
    
    Details:
    - ID: {answer_type['id']}
    - Keywords: {answer_type['keywords'] or 'None'}
    - Sort Order: {answer_type['sort'] or 'Not specified'}
    - Status: {'Active' if answer_type['is_valid'] else 'Inactive'}
    - Revision: {answer_type['revision'] or 0}
    
    Created: {answer_type['create_date'] or 'Unknown'}
    Last Updated: {answer_type['update_date'] or 'Unknown'}
    
    This answer type can be used in educational assessments and quizzes within the LMS system.
    """
    
    return explanation

def run_mcp_server(
    transport: Literal["stdio", "sse"] = "stdio",
    host: str = "localhost", 
    port: int = 8001
):
    """
    Run the MCP server with configurable transport.
    
    Args:
        transport: Transport type - "stdio" (default) or "sse"
        host: Host for SSE transport (default: localhost)
        port: Port for SSE transport (default: 8001)
    """
    print(f"Starting LMS MCP Server with {transport.upper()} transport...")
    
    if transport == "stdio":
        # STDIO transport - for process-based clients like Claude Desktop
        print("Running with STDIO transport (best for Claude Desktop)")
        mcp.run()
    elif transport == "sse":
        # SSE transport - for web-based streaming clients
        print(f"Running with SSE transport on {host}:{port}")
        print(f"SSE endpoint: http://{host}:{port}/sse")
        mcp.run(transport="sse")
    else:
        raise ValueError(f"Unsupported transport: {transport}")

if __name__ == "__main__":
    # Parse command line arguments for transport selection
    transport = "stdio"  # default
    host = "localhost"
    port = 8001
    
    if len(sys.argv) > 1:
        if sys.argv[1] in ["stdio", "sse"]:
            transport = sys.argv[1]
        else:
            print("Usage: python mcp_server.py [stdio|sse] [host] [port]")
            sys.exit(1)
    
    if len(sys.argv) > 2:
        host = sys.argv[2]
    
    if len(sys.argv) > 3:
        port = int(sys.argv[3])
    
    run_mcp_server(transport, host, port) 
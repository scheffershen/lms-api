#!/usr/bin/env python3
"""
Startup script for the LMS MCP Server

This script starts the MCP server that exposes LMS API functionality
to LLMs through the Model Context Protocol.
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.mcp_server import run_mcp_server

if __name__ == "__main__":
    run_mcp_server() 
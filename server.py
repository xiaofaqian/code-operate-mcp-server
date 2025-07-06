#!/usr/bin/env python3
"""
Code Operation MCP Server using FastMCP
"""

import logging
from mcp.server.fastmcp import FastMCP

# 导入工具模块
from tools import read_text_file, replace_code_by_line, create_file, search_in_file

# Configure logging for comprehensive error tracking
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-server")

# Create FastMCP server instance
mcp = FastMCP("code-operate-mcp-server")

# 注册工具
mcp.tool()(read_text_file)
mcp.tool()(replace_code_by_line)
mcp.tool()(create_file)
mcp.tool()(search_in_file)

if __name__ == "__main__":
    logger.info("[Setup] Initializing Code Operation MCP Server...")
    mcp.run()

import os
import httpx
import json

from mcp.server.fastmcp import FastMCP

from config import app_config


mcp = FastMCP(
    name="mataparser",
)

@mcp.tool()
async def tool_parse(file_path: str, json_template: str) -> dict:
    """
    Parse or extract document or image into structured JSON using Mataparser API.

    :param file_path: Path to the file to parse
    :param json_template: Custom JSON format
    :return: Parsed JSON result or error object
    """
    api_key: str = app_config.API_KEY

    # Check API Key
    if not api_key:
        return {
            "success": False,
            "error": "API_KEY_REQUIRED",
            "message": "API key is required",
        }

    # Verify JSON template
    if not json_template:
        return {
            "success": False,
            "error": "JSON_TEMPLATE_REQUIRED",
            "message": "JSON template is required",
        }
    
    try:
        json.loads(json_template)
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": "INVALID_JSON_TEMPLATE",
            "message": f"Invalid JSON template: {str(e)}",
        }

    # File existence check - handle both absolute and relative paths
    if os.path.isabs(file_path):
        abs_path = file_path
    else:
        abs_path = os.path.abspath(file_path)

    if not os.path.exists(abs_path):
        return {
            "success": False,
            "error": "FILE_NOT_FOUND",
            "message": f"File not found: {abs_path}. Please ensure the file is accessible from the MCP server location.",
        }

    # Extension validation
    ext = os.path.splitext(abs_path)[1].lower()

    if ext not in app_config.ALLOWED_EXTENSIONS:
        return {
            "success": False,
            "error": "INVALID_FILE_TYPE",
            "message": f"Unsupported file type: {ext}",
            "allowed_extensions": list(app_config.ALLOWED_EXTENSIONS),
        }

    # File size validation
    file_size_mb = os.path.getsize(abs_path) / (1024 * 1024)

    if file_size_mb > app_config.MAX_FILE_SIZE_MB:
        return {
            "success": False,
            "error": "FILE_TOO_LARGE",
            "message": f"File size {file_size_mb:.2f}MB exceeds {app_config.MAX_FILE_SIZE_MB}MB limit",
        }

    headers = {
        "x-api-key": api_key,
    }

    data = {
        "json_template": json_template,
    }

    try:
        async with httpx.AsyncClient() as client:
            with open(abs_path, "rb") as f:
                files = {
                    "file": (os.path.basename(abs_path), f)
                }

                # Sending the request with authentication headers
                response = await client.post(
                    f"{app_config.API_URL}/parse",
                    headers=headers,
                    files=files,
                    data=data,
                    timeout=30.0,
                )

        # Handle non-2xx responses cleanly
        if response.status_code >= 400:
            return {
                "success": False,
                "error": "API_ERROR",
                "status_code": response.status_code,
                "message": response.text,
            }

        return {
            "success": True,
            "data": response.json(),
            "metadata": {
                "filename": os.path.basename(abs_path),
                "file_size_mb": round(file_size_mb, 2),
            },
        }
    except httpx.TimeoutException:
        return {
            "success": False,
            "error": "TIMEOUT",
            "message": "Request to Mataparser API timed out",
        }
    except httpx.RequestError as e:
        return {
            "success": False,
            "error": "REQUEST_ERROR",
            "message": str(e),
        }
    except Exception as e:
        return {
            "success": False,
            "error": "INTERNAL_ERROR",
            "message": str(e),
        }


if __name__ == "__main__":
    mcp.run(transport="stdio")

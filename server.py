import json
from enum import Enum
from contextlib import asynccontextmanager
from fastmcp import FastMCP, Context
from browser_manager import PersistentBrowserManager
from token_trimmer import HybridTokenTrimmer

class ErrorCode(str, Enum):
    TIMEOUT = "TIMEOUT"
    BOT_BLOCKED = "BOT_BLOCKED"
    SHADOW_DOM_MISS = "SHADOW_DOM_MISS"
    INTERNAL_CRASH = "INTERNAL_CRASH"
    TOKEN_OVERFLOW = "TOKEN_OVERFLOW"

def format_error(code: ErrorCode, message: str, suggestion: str) -> str:
    """Returns structured JSON for errors to prevent unrecoverable crashes across the MCP boundary."""
    return json.dumps({
        "status": "error",
        "error_code": code.value,
        "message": message,
        "recoverable": True,
        "suggestion": suggestion
    })

# Initialize Trimmer globally
trimmer = HybridTokenTrimmer(max_tokens=25000)

@asynccontextmanager
async def browser_lifespan(server: FastMCP):
    """Initializes the browser engine exactly once on startup."""
    manager = PersistentBrowserManager()
    await manager.start()
    try:
        # Yield the manager to the context so tools can access it
        yield {"browser": manager}
    finally:
        await manager.stop()

# Instantiate FastMCP with the strict lifespan context manager
mcp = FastMCP("ResilientResearch", lifespan=browser_lifespan)

@mcp.tool()
async def browser_navigate(url: str, ctx: Context) -> str:
    """
    Navigates the persistent browser to a URL. 
    Call this first to load a page.
    """
    browser: PersistentBrowserManager = ctx.request_context.lifespan_context["browser"]
    try:
        result = await browser.navigate(url)
        if result["status"] == "error":
            return format_error(ErrorCode.TIMEOUT, result["message"], "Check URL or wait longer.")
        return json.dumps(result)
    except Exception as e:
        return format_error(ErrorCode.INTERNAL_CRASH, str(e), "Retry navigation.")

@mcp.tool()
async def browser_extract(schema_description: str, ctx: Context) -> str:
    """
    Extracts the current page content and applies Token-Aware Trimming.
    The LLM (Claude) should pass a description of the desired Pydantic schema,
    and this tool will return deeply cleaned, token-safe Markdown for Claude to parse.
    """
    browser: PersistentBrowserManager = ctx.request_context.lifespan_context["browser"]
    try:
        result = await browser.extract_raw_html()
        if result["status"] == "error":
            return format_error(ErrorCode.SHADOW_DOM_MISS, result["message"], "Check if page has loaded.")
        
        # Process the raw HTML into token-safe Markdown
        clean_markdown = trimmer.process(result["html"])
        
        return clean_markdown
    except Exception as e:
        return format_error(ErrorCode.INTERNAL_CRASH, str(e), "Extraction failed.")

if __name__ == "__main__":
    mcp.run()

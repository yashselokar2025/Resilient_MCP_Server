# Resilient Research MCP Server

> **"I built a Python MCP server that gives Claude a persistent, stealth-capable browser. Unlike standard implementations which dump raw HTML and cold-start per call, mine maintains session state across tool calls (enabling multi-step flows), accepts JSON extraction schemas for typed structured data, and applies token-aware trimming to avoid context window blowouts. Built with FastMCP, Playwright async API, and playwright-stealth."**

## Why This Exists (Solving the 5 Agentic Gaps)

Standard "navigate and read" browser automation tutorials fail in production AI environments. This server was architected from the ground up to solve the 5 major gaps in modern LLM browser interaction:

1. **Token Explosion:** Dumps of raw HTML crash LLM context windows. 
   * **Solution:** A `HybridTokenTrimmer` that uses local character estimation (`len // 4`) for zero-latency checks, falling back to Anthropic's API only when nearing the 25k token threshold to intelligently truncate output.
2. **Shadow DOM Blindness:** Modern components (React/Shoelace) hide data in closed/open shadow roots that standard Playwright cannot read.
   * **Solution:** Custom JavaScript injection that recursively pierces open `shadowRoot` boundaries and extracts the contents into the light DOM before parsing.
3. **Anti-Bot Blocking:** Vanilla headless browsers are instantly blocked by Cloudflare.
   * **Solution:** Explicit integration with `playwright-stealth v2.x` to mask headless signatures, successfully bypassing mid-tier Cloudflare JS challenges.
4. **No Session State (Cold Starts):** Standard MCP servers spin up a fresh browser for every tool call, breaking multi-step flows.
   * **Solution:** A `PersistentBrowserManager` that maintains a Singleton Playwright context, enabling Claude to `navigate`, `scroll`, and `extract` sequentially within the exact same window.
5. **Concurrency Crashes:** FastMCP executes tools in parallel, causing Playwright to crash with "Navigation already in progress" errors.
   * **Solution:** Implementation of `asyncio.Lock()` to strictly serialize access to the active page, allowing safe, queued execution of parallel agent commands.

## Tech Stack
* **Framework:** [FastMCP 3.0](https://github.com/jlowin/fastmcp)
* **Browser Engine:** Playwright Async API
* **Stealth:** `playwright-stealth` (v2.x)
* **HTML Parsing:** `markdownify` & `BeautifulSoup4`

## Setup & Installation

1. Clone the repository and navigate to the directory:
   ```bash
   git clone https://github.com/yashselokar2025/Week-4-blank.git
   cd Resilient_MCP_Server
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```
3. Install dependencies and Playwright binaries:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

## Running the Server

Start the FastMCP server so Claude can connect to it:
```bash
python server.py
```

## Running the Verification Tests

This project includes 4 hardened verification scripts to prove the architecture under stress:

* `python test_stealth.py` - Verifies the anti-bot module against a live Cloudflare-protected site.
* `python test_shadow_dom.py` - Verifies the recursive JS extraction against an isolated Shadow Root.
* `python test_token_overflow.py` - Verifies the `HybridTokenTrimmer` successfully strips CSS/JS nodes and truncates the massive Wikipedia "World War II" page.
* `python test_concurrency.py` - Stress-tests the `asyncio.Lock()` by firing 3 simultaneous browser actions to ensure Playwright queues them instead of crashing.

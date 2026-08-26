import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

class PersistentBrowserManager:
    """
    Manages a singleton Playwright browser session.
    Implements asyncio.Lock() to prevent race conditions during concurrent FastMCP tool calls.
    """
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        # CRITICAL FIX: Serializes access to the active page
        self.lock = asyncio.Lock()

    async def start(self):
        """Initializes the browser and applies stealth."""
        self.playwright = await async_playwright().start()
        # Launch headless chromium
        self.browser = await self.playwright.chromium.launch(headless=True)
        # Create a persistent context
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        
        # Inject playwright-stealth to bypass basic Cloudflare/bot protections
        await Stealth().apply_stealth_async(self.page)
        print("[BrowserManager] Started persistent stealth session.")

    async def stop(self):
        """Teardown browser gracefully."""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        print("[BrowserManager] Stopped session.")

    async def navigate(self, url: str) -> dict:
        """Navigates to a URL safely using the lock."""
        async with self.lock:
            try:
                print(f"[BrowserManager] Navigating to {url}")
                # Use domcontentloaded instead of networkidle because Cloudflare challenges 
                # keep network active, causing timeouts.
                await self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
                return {"status": "success", "url": url}
            except Exception as e:
                # We return structured JSON for the Error Taxonomy to handle later
                return {"status": "error", "error_type": "TIMEOUT_OR_NETWORK", "message": str(e)}

    async def extract_raw_html(self) -> dict:
        """
        Pierces Shadow DOM boundaries and extracts the full HTML.
        Returns a dict so we can safely catch errors.
        """
        async with self.lock:
            try:
                # Inject JS to recursively build HTML string piercing through Shadow DOMs
                shadow_pierce_script = """
                () => {
                    function getPiercedHTML(node) {
                        let html = "";
                        for (let child of node.childNodes) {
                            if (child.nodeType === Node.ELEMENT_NODE) {
                                html += `<${child.tagName.toLowerCase()}`;
                                for (let attr of child.attributes) {
                                    html += ` ${attr.name}="${attr.value}"`;
                                }
                                html += ">";
                                if (child.shadowRoot) {
                                    html += getPiercedHTML(child.shadowRoot);
                                } else {
                                    html += getPiercedHTML(child);
                                }
                                html += `</${child.tagName.toLowerCase()}>`;
                            } else if (child.nodeType === Node.TEXT_NODE) {
                                html += child.textContent;
                            }
                        }
                        return html;
                    }
                    return getPiercedHTML(document.body);
                }
                """
                print("[BrowserManager] Piercing Shadow DOM and extracting HTML...")
                modified_html = await self.page.evaluate(shadow_pierce_script)
                return {"status": "success", "html": modified_html}
            except Exception as e:
                return {"status": "error", "error_type": "EXTRACTION_FAILED", "message": str(e)}

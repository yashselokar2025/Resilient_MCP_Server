import asyncio
from browser_manager import PersistentBrowserManager

async def run_stealth_test():
    manager = PersistentBrowserManager()
    await manager.start()
    
    print("[Test 1: Anti-Bot Stealth]")
    print("Navigating to https://nowsecure.nl (Cloudflare protected)...")
    
    # nowsecure.nl is a standard test page for playwright-stealth
    result = await manager.navigate("https://nowsecure.nl")
    if result["status"] == "error":
        print(f"FAILED to navigate: {result['message']}")
        await manager.stop()
        return

    # Wait an extra few seconds for Cloudflare JS challenge to theoretically pass
    await asyncio.sleep(5)
    
    extraction = await manager.extract_raw_html()
    html = extraction.get("html", "")
    
    if "OH YEAH, you passed" in html or "nowsecure.nl" in html.lower():
        print("SUCCESS! Successfully bypassed Cloudflare protection using playwright-stealth v2.x")
    elif "Just a moment" in html or "cloudflare" in html.lower():
        print("FAILED! Detected by Cloudflare. Stealth failed.")
        print("Preview of failure page:", html[:200])
    else:
        print("UNKNOWN Result. Here is a snippet of the page:")
        print(html[:300])

    await manager.stop()

if __name__ == "__main__":
    asyncio.run(run_stealth_test())

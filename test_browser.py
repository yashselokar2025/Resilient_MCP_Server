import asyncio
from browser_manager import PersistentBrowserManager

async def test_browser():
    manager = PersistentBrowserManager()
    print("Starting browser...")
    await manager.start()
    
    print("Navigating to example.com...")
    nav_result = await manager.navigate("https://example.com")
    print(f"Navigation Result: {nav_result}")
    
    print("Extracting HTML...")
    extract_result = await manager.extract_raw_html()
    
    if extract_result["status"] == "success":
        html_snippet = extract_result["html"][:100].replace('\n', ' ')
        print(f"Extraction Success! Snippet: {html_snippet}...")
    else:
        print(f"Extraction Failed: {extract_result}")
        
    print("Stopping browser...")
    await manager.stop()

if __name__ == "__main__":
    asyncio.run(test_browser())

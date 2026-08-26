import asyncio
from browser_manager import PersistentBrowserManager
from token_trimmer import HybridTokenTrimmer

async def run_token_overflow_test():
    manager = PersistentBrowserManager()
    
    # We set a deliberately low threshold (e.g. 1000 tokens) to guarantee the 
    # Wikipedia page triggers both the local estimate and the API fallback truncation
    trimmer = HybridTokenTrimmer(max_tokens=1000)
    
    await manager.start()
    
    print("[Test 3: Token Overflow & Trimming]")
    print("Navigating to Wikipedia (Massive page)...")
    
    # The World War II wikipedia page is massive (easily > 20k words)
    result = await manager.navigate("https://en.wikipedia.org/wiki/World_War_II")
    if result["status"] == "error":
        print(f"FAILED to navigate: {result['message']}")
        await manager.stop()
        return

    extraction = await manager.extract_raw_html()
    html = extraction.get("html", "")
    
    print("Processing HTML through Token Trimmer...")
    clean_markdown = trimmer.process(html)
    
    if "[WARNING: TRUNCATED" in clean_markdown or "[!WARNING]" in clean_markdown:
        print("SUCCESS! The Hybrid Token Trimmer successfully detected the overflow and truncated the output to prevent a context window crash.")
        print(f"Final output length: {len(clean_markdown)} characters.")
    else:
        print("FAILED! The trimmer failed to truncate the massively oversized document.")
        
    await manager.stop()

if __name__ == "__main__":
    asyncio.run(run_token_overflow_test())

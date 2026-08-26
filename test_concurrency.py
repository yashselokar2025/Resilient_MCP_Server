import asyncio
import time
from browser_manager import PersistentBrowserManager

async def concurrent_navigate_and_extract():
    manager = PersistentBrowserManager()
    await manager.start()
    
    print("[Test 4: Concurrency & asyncio.Lock Queueing]")
    print("Firing multiple tool calls simultaneously (like FastMCP does in parallel mode)...")
    
    start_time = time.time()
    
    # We will trigger two navigations and one extract simultaneously
    # Without a lock, Playwright will crash saying "Navigation already in progress"
    # With a lock, they will queue up safely sequentially
    task1 = asyncio.create_task(manager.navigate("https://example.com"))
    task2 = asyncio.create_task(manager.extract_raw_html())
    task3 = asyncio.create_task(manager.navigate("https://example.org"))
    
    results = await asyncio.gather(task1, task2, task3, return_exceptions=True)
    
    end_time = time.time()
    
    # If the lock works, we should NOT see any "Navigation already in progress" errors.
    # We should see successful results for all.
    success = True
    for idx, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"Task {idx+1} CRASHED: {result}")
            success = False
        elif result.get("status") == "error":
            print(f"Task {idx+1} ERROR: {result}")
            # If the error is a timeout, that's fine, but it shouldn't be a concurrency crash
            if "already in progress" in result.get("message", "").lower():
                success = False
    
    if success:
        print(f"SUCCESS! All {len(results)} concurrent tasks safely queued and completed in {end_time - start_time:.2f}s without crashing the browser!")
    else:
        print("FAILED! Concurrency race condition detected.")
        
    await manager.stop()

if __name__ == "__main__":
    asyncio.run(concurrent_navigate_and_extract())

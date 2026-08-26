import asyncio
from browser_manager import PersistentBrowserManager

async def run_shadow_dom_test():
    manager = PersistentBrowserManager()
    await manager.start()
    
    print("[Test 2: Shadow DOM Piercing]")
    # Lit element official playground has heavy Shadow DOM usage
    print("Navigating to a local isolated Shadow DOM test page...")
    
    # Create a local test page using a data URI that explicitly creates an open shadow root
    # containing a secret hidden message.
    shadow_dom_html = """
    <!DOCTYPE html>
    <html>
    <body>
        <div id="host"></div>
        <script>
            const host = document.getElementById('host');
            const shadow = host.attachShadow({mode: 'open'});
            shadow.innerHTML = '<p id="secret">SHADOW_SECRET_12345</p>';
        </script>
    </body>
    </html>
    """
    import urllib.parse
    data_uri = "data:text/html;charset=utf-8," + urllib.parse.quote(shadow_dom_html)
    
    result = await manager.navigate(data_uri)
    if result["status"] == "error":
        print(f"FAILED to navigate: {result['message']}")
        await manager.stop()
        return

    # Wait for JS to run
    await asyncio.sleep(1)
    
    extraction = await manager.extract_raw_html()
    html = extraction.get("html", "")
    
    if "SHADOW_SECRET_12345" in html:
        print("SUCCESS! The Shadow DOM was successfully pierced and its contents extracted to the light DOM.")
    else:
        print("FAILED! Shadow DOM elements were not pierced.")
        print(f"Extracted HTML: {html}")
        
    await manager.stop()

if __name__ == "__main__":
    asyncio.run(run_shadow_dom_test())

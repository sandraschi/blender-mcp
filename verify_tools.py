import httpx
import json
import asyncio

async def verify():
    url = "http://127.0.0.1:10849/mcp"
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    }
    
    headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json"
    }
    
    print(f"Connecting to {url}...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers, timeout=10.0)

            if response.status_code == 200:
                data = response.json()
                if "result" in data and "tools" in data["result"]:
                    tools = data["result"]["tools"]
                    print(f"Successfully retrieved {len(tools)} tools:")
                    for tool in tools:
                        print(f" - {tool['name']}: {tool.get('description', 'No description')[:50]}...")
                    
                    # Check for specific tools we expect
                    tool_names = [t["name"] for t in tools]
                    expected = ["blender_materials", "create_scene", "list_scenes"]
                    for e in expected:
                        if e in tool_names:
                            print(f" ✓ Tool '{e}' is registered.")
                        else:
                            print(f" ✗ Tool '{e}' is MISSING!")
                else:
                    print("Unexpected response format:")
                    print(json.dumps(data, indent=2))
            else:
                print(f"Error: Status code {response.status_code}")
                print(response.text)
    except Exception as e:
        print(f"Verification failed: {e}")

if __name__ == "__main__":
    asyncio.run(verify())

import httpx
import asyncio
import os

async def test():
    async with httpx.AsyncClient(
        base_url="http://localhost:8000",
        timeout=httpx.Timeout(120.0, connect=10.0)
    ) as client:
        # Login
        r = await client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        }, follow_redirects=False)
        print(f"Login: {r.status_code}")
        
        # Create channel
        r = await client.post("/api/channels", json={
            "name": "Test Channel",
            "description": "Test description"
        })
        print(f"Create channel: {r.status_code} {r.text[:200]}")
        
        # Get channel
        r = await client.get("/api/channels/me")
        print(f"Get channel: {r.status_code} {r.text[:200]}")
        
        # Check file exists
        filepath = r"D:\DJ\Футажи\Футажи Донескин\Halloween\Halloween.mp4"
        print(f"File exists: {os.path.exists(filepath)}")
        if os.path.exists(filepath):
            print(f"File size: {os.path.getsize(filepath)} bytes")
        
        # Upload video
        print("Starting upload...")
        with open(filepath, "rb") as f:
            print(f"Opening file, size: {os.path.getsize(filepath)}")
            files = {"video_file": ("Halloween.mp4", f, "video/mp4")}
            data = {
                "title": "Test Halloween Video",
                "description": "Test video for MinIO upload",
                "privacy": "public"
            }
            print("Sending request...")
            r = await client.post("/api/videos/upload", data=data, files=files)
            print(f"Upload response: {r.status_code}")
            print(f"Response body: {r.text[:1000]}")
            
            if r.status_code == 201:
                video_data = r.json()
                print(f"\nVideo URL: {video_data.get('video_url')}")
                
                # Try to get the video
                video_id = video_data.get("id")
                r2 = await client.get(f"/api/videos/{video_id}")
                print(f"\nGet video: {r2.status_code}")
                if r2.status_code == 200:
                    v = r2.json()
                    print(f"Video URL from API: {v.get('video_url')}")

asyncio.run(test())

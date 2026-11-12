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
        
        # Upload video
        filepath = r"D:\DJ\Футажи\Футажи Донескин\Halloween\Halloween.mp4"
        print(f"File size: {os.path.getsize(filepath)} bytes")
        
        with open(filepath, "rb") as f:
            files = {"video_file": ("Halloween.mp4", f, "video/mp4")}
            data = {
                "title": "Test Halloween Video 2",
                "description": "Test video for MinIO upload - second test",
                "privacy": "public"
            }
            r = await client.post("/api/videos/upload", data=data, files=files)
            print(f"Upload: {r.status_code}")
            video = r.json()
            print(f"Video ID: {video['id']}")
            print(f"Video URL: {video['video_url']}")
            
            # Get video
            r2 = await client.get(f"/api/videos/{video['id']}")
            print(f"\nGet video: {r2.status_code}")
            
            # Check file in MinIO
            r3 = await client.get(video['video_url'])
            print(f"MinIO file: status={r3.status_code}, size={len(r3.content)} bytes")
            
            # Check HTML page
            r4 = await client.get(f"/video/{video['id']}")
            print(f"\nHTML page: {r4.status_code}")
            if r4.status_code == 200:
                # Check if video URL is in the page
                if video['video_url'] in r4.text:
                    print("Video URL found in HTML page!")
                else:
                    print("Video URL NOT found in HTML page")

asyncio.run(test())

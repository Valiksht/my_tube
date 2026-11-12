import httpx
import asyncio

async def test():
    # Test MinIO connection directly
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Test MinIO health
        r = await client.get("http://localhost:9000/minio/health/live")
        print(f"MinIO health: {r.status_code}")
        
        # Test bucket exists via API
        r = await client.get("http://localhost:9000/videos?location=")
        print(f"Bucket location: {r.status_code} {r.text[:200]}")
        
        # Test list buckets
        r = await client.get("http://localhost:9000/?buckets=")
        print(f"List buckets: {r.status_code} {r.text[:500]}")

asyncio.run(test())

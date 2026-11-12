import subprocess
result = subprocess.run(
    ["docker", "exec", "mytube_api_local", "python", "-c", """
from minio import Minio
import os

client = Minio(
    os.getenv("MINIO_HOST", "localhost"),
    access_key=os.getenv("MINIO_ROOT_USER", "minioadmin"),
    secret_key=os.getenv("MINIO_ROOT_PASSWORD", "minioadmin"),
    secure=os.getenv("MINIO_SECURE", "false").lower() == "true",
)

print(f"Connecting to: {os.getenv('MINIO_HOST', 'localhost')}")
print(f"Secure: {os.getenv('MINIO_SECURE', 'false')}")

try:
    buckets = client.list_buckets()
    print(f"Buckets: {[b.name for b in buckets]}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
"""],
    capture_output=True, text=True
)
print(result.stdout)
print("STDERR:", result.stderr)

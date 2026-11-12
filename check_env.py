import subprocess
result = subprocess.run(
    ["docker", "exec", "mytube_api_local", "python", "-c", """
import os
print("MINIO_HOST:", os.getenv("MINIO_HOST"))
print("MINIO_PUBLIC_URL:", os.getenv("MINIO_PUBLIC_URL"))
print("MINIO_SECURE:", os.getenv("MINIO_SECURE"))
print("STORAGE_TYPE:", os.getenv("STORAGE_TYPE"))
print("MINIO_ROOT_USER:", os.getenv("MINIO_ROOT_USER"))
print("MINIO_ROOT_PASSWORD:", os.getenv("MINIO_ROOT_PASSWORD"))
print("MINIO_BUCKET:", os.getenv("MINIO_BUCKET"))
"""],
    capture_output=True, text=True
)
print(result.stdout)
print("STDERR:", result.stderr)

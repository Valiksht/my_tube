import subprocess
result = subprocess.run(
    ["docker", "exec", "mytube_api_local", "python", "-c", 
     "from app.storage.factory import get_storage; s = get_storage(); print('Type:', type(s).__name__); print('Bucket:', s.bucket); print('Exists:', s.client.bucket_exists(s.bucket))"],
    capture_output=True, text=True
)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)

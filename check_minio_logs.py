import subprocess
result = subprocess.run(
    ["docker", "logs", "mytube_minio_local"],
    capture_output=True, text=True, errors='replace'
)
print(result.stdout[-3000:])

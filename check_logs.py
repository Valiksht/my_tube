import subprocess
result = subprocess.run(
    ["docker", "logs", "mytube_api_local"],
    capture_output=True, text=True, errors='replace'
)
lines = result.stdout.split('\n')
for i, line in enumerate(lines):
    if 'upload' in line.lower() or 'minio' in line.lower() or 'rollback' in line.lower() or '500' in line:
        start = max(0, i - 2)
        end = min(len(lines), i + 3)
        print(f'\nLine {i}:')
        for j in range(start, end):
            print(f'  {j}: {lines[j]}')

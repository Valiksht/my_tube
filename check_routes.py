"""Script to list all routes from OpenAPI schema."""

from app.main import app
import json


# Generate OpenAPI schema
schema = app.openapi()

print(f"App: {schema['info']['title']}")
print(f"Version: {schema['info']['version']}")
print()

paths = schema.get("paths", {})
print(f"Total API paths: {len(paths)}")
print()

for path, methods in sorted(paths.items()):
    for method, details in methods.items():
        if method in ("get", "post", "put", "patch", "delete", "head", "options", "trace"):
            summary = details.get("summary", "")
            print(f"{method.upper():8s} {path:50s} {summary}")

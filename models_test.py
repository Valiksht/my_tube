"""Test models imports and configuration."""
import sys
sys.path.insert(0, '.')

from app.models.base import Base
from app.models.user import User
from app.models.channel import Channel
from app.models.video import Video
from app.models.like import Like
from app.models.comment import Comment
from app.models.subscription import Subscription

from sqlalchemy.orm import configure_mappers

# Check imports work
print("=== Model Imports Test ===")
print(f"✓ Base: {Base}")
print(f"✓ User: {User.__tablename__}")
print(f"✓ Channel: {Channel.__tablename__}")
print(f"✓ Video: {Video.__tablename__}")
print(f"✓ Like: {Like.__tablename__}")
print(f"✓ Comment: {Comment.__tablename__}")
print(f"✓ Subscription: {Subscription.__tablename__}")

# Configure mappers
configure_mappers()
print("\n=== configure_mappers() completed successfully ===")

# Check tables in metadata
print("\n=== Tables in Base.metadata ===")
for table_name in sorted(Base.metadata.tables.keys()):
    print(f"  ✓ {table_name}")

print("\n=== All tests passed! ===")
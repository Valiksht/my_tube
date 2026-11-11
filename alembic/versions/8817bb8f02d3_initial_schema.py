"""initial schema

Revision ID: 8817bb8f02d3
Revises: 
Create Date: 2026-11-11 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8817bb8f02d3'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=256), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('role', sa.String(length=20), nullable=False, default='user'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email'),
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_role'), 'users', ['role'], unique=False)
    
    # channels
    op.create_table(
        'channels',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False, default=''),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('banner_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.UniqueConstraint('user_id'),
    )
    op.create_index(op.f('ix_channels_id'), 'channels', ['id'], unique=False)
    op.create_index(op.f('ix_channels_name'), 'channels', ['name'], unique=False)
    op.create_index(op.f('ix_channels_user_id'), 'channels', ['user_id'], unique=False)
    
    # videos
    op.create_table(
        'videos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('channel_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True, default=''),
        sa.Column('video_url', sa.String(length=500), nullable=True),
        sa.Column('video_object_name', sa.String(length=500), nullable=True),
        sa.Column('thumbnail_url', sa.String(length=500), nullable=True),
        sa.Column('thumbnail_object_name', sa.String(length=500), nullable=True),
        sa.Column('duration', sa.Integer(), nullable=True, default=0),
        sa.Column('view_count', sa.Integer(), nullable=True, default=0),
        sa.Column('privacy', sa.String(length=10), nullable=False, default='public'),
        sa.Column('is_published', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['channel_id'], ['channels.id'], ),
    )
    op.create_index(op.f('ix_videos_id'), 'videos', ['id'], unique=False)
    op.create_index(op.f('ix_videos_channel_id'), 'videos', ['channel_id'], unique=False)
    
    # user_sessions
    op.create_table(
        'user_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(length=64), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.String(length=1), nullable=False, default='1'),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('session_id'),
    )
    op.create_index(op.f('ix_user_sessions_id'), 'user_sessions', ['id'], unique=False)
    op.create_index(op.f('ix_user_sessions_session_id'), 'user_sessions', ['session_id'], unique=True)
    op.create_index(op.f('ix_user_sessions_user_id'), 'user_sessions', ['user_id'], unique=False)
    
    # comments
    op.create_table(
        'comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('video_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.String(length=2000), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    )
    op.create_index(op.f('ix_comments_id'), 'comments', ['id'], unique=False)
    op.create_index(op.f('ix_comments_video_id'), 'comments', ['video_id'], unique=False)
    op.create_index(op.f('ix_comments_user_id'), 'comments', ['user_id'], unique=False)
    
    # likes
    op.create_table(
        'likes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('video_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.UniqueConstraint('user_id', 'video_id', name='uq_user_video_likes'),
    )
    op.create_index(op.f('ix_likes_id'), 'likes', ['id'], unique=False)
    op.create_index(op.f('ix_likes_video_id'), 'likes', ['video_id'], unique=False)
    op.create_index(op.f('ix_likes_user_id'), 'likes', ['user_id'], unique=False)
    
    # subscriptions
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('subscribed_user_id', sa.Integer(), nullable=False),
        sa.Column('subscribed_channel_id', sa.Integer(), nullable=False),
        sa.Column('notification_enabled', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['subscribed_user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['subscribed_channel_id'], ['channels.id'], ),
        sa.UniqueConstraint('subscribed_user_id', 'subscribed_channel_id', name='uq_user_channel_subscription'),
    )
    op.create_index(op.f('ix_subscriptions_id'), 'subscriptions', ['id'], unique=False)
    op.create_index(op.f('ix_subscriptions_subscribed_user_id'), 'subscriptions', ['subscribed_user_id'], unique=False)
    op.create_index(op.f('ix_subscriptions_subscribed_channel_id'), 'subscriptions', ['subscribed_channel_id'], unique=False)
    
    # reports
    op.create_table(
        'reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('reporter_id', sa.Integer(), nullable=False),
        sa.Column('target_type', sa.String(length=10), nullable=False),
        sa.Column('target_id', sa.Integer(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('moderator_id', sa.Integer(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('moderator_notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['reporter_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['moderator_id'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index(op.f('ix_reports_id'), 'reports', ['id'], unique=False)
    op.create_index(op.f('ix_reports_reporter_id'), 'reports', ['reporter_id'], unique=False)
    
    # hidden_content
    op.create_table(
        'hidden_content',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content_type', sa.String(length=10), nullable=False),
        sa.Column('content_id', sa.Integer(), nullable=False),
        sa.Column('moderator_id', sa.Integer(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('hidden_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['moderator_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index(op.f('ix_hidden_content_id'), 'hidden_content', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('hidden_content')
    op.drop_table('reports')
    op.drop_table('subscriptions')
    op.drop_table('likes')
    op.drop_table('comments')
    op.drop_table('user_sessions')
    op.drop_table('videos')
    op.drop_table('channels')
    op.drop_table('users')

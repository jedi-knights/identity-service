"""Initial database schema

Revision ID: 91e3dcbe3e16
Revises: 
Create Date: 2026-02-11 11:05:38.238279

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '91e3dcbe3e16'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('username', sa.String(100), unique=True, nullable=False, index=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # Create clients table
    op.create_table(
        'clients',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('client_name', sa.String(255), nullable=False),
        sa.Column('client_secret_hash', sa.String(255), nullable=False),
        sa.Column('redirect_uris', sa.dialects.postgresql.ARRAY(sa.Text()), nullable=False),
        sa.Column('grant_types', sa.dialects.postgresql.ARRAY(sa.String(50)), nullable=False),
        sa.Column('scopes', sa.dialects.postgresql.ARRAY(sa.String(100)), nullable=False, server_default='{}'),
        sa.Column('is_confidential', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # Create tokens table
    op.create_table(
        'tokens',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('client_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('access_token', sa.Text(), unique=True, nullable=False, index=True),
        sa.Column('token_type', sa.String(50), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('scopes', sa.dialects.postgresql.ARRAY(sa.String(100)), nullable=False),
        sa.Column('refresh_token', sa.Text(), unique=True, nullable=True, index=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('tokens')
    op.drop_table('clients')
    op.drop_table('users')

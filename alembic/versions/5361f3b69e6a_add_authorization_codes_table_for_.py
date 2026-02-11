"""Add authorization codes table for OAuth2 authorization code flow

Revision ID: 5361f3b69e6a
Revises: 91e3dcbe3e16
Create Date: 2026-02-11 06:29:03.310876

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5361f3b69e6a"
down_revision: Union[str, Sequence[str], None] = "91e3dcbe3e16"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "authorization_codes",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("code", sa.String(length=255), nullable=False),
        sa.Column("client_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=True),
        sa.Column("redirect_uri", sa.Text(), nullable=False),
        sa.Column("scopes", sa.ARRAY(sa.String(length=100)), nullable=False),
        sa.Column("code_challenge", sa.String(length=255), nullable=True),
        sa.Column("code_challenge_method", sa.String(length=10), nullable=True),
        sa.Column("state", sa.String(length=255), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("is_used", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_authorization_codes_client_id"), "authorization_codes", ["client_id"], unique=False
    )
    op.create_index(
        op.f("ix_authorization_codes_code"), "authorization_codes", ["code"], unique=True
    )
    op.create_index(
        op.f("ix_authorization_codes_expires_at"),
        "authorization_codes",
        ["expires_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_authorization_codes_user_id"), "authorization_codes", ["user_id"], unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_authorization_codes_user_id"), table_name="authorization_codes")
    op.drop_index(op.f("ix_authorization_codes_expires_at"), table_name="authorization_codes")
    op.drop_index(op.f("ix_authorization_codes_code"), table_name="authorization_codes")
    op.drop_index(op.f("ix_authorization_codes_client_id"), table_name="authorization_codes")
    op.drop_table("authorization_codes")

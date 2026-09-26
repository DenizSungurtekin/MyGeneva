"""add events.is_promoted

Revision ID: 77e5eb8019bf
Revises: c8a15d07cecd
Create Date: 2026-09-26 14:07:31.222574

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '77e5eb8019bf'
down_revision: Union[str, None] = 'c8a15d07cecd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                'is_promoted',
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )
        batch_op.create_index(batch_op.f('ix_events_is_promoted'), ['is_promoted'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_events_is_promoted'))
        batch_op.drop_column('is_promoted')

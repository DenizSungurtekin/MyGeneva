"""add events.dedup_key and alt_source_urls

Revision ID: 580ed6bb9ccd
Revises: 1442e094f138
Create Date: 2026-09-26 15:47:28.198144

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


revision: str = '580ed6bb9ccd'
down_revision: Union[str, None] = '1442e094f138'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.add_column(sa.Column('dedup_key', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
        batch_op.add_column(sa.Column('alt_source_urls', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
        batch_op.create_index(batch_op.f('ix_events_dedup_key'), ['dedup_key'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_events_dedup_key'))
        batch_op.drop_column('alt_source_urls')
        batch_op.drop_column('dedup_key')

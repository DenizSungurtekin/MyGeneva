"""add places.google_place_id

Revision ID: 1442e094f138
Revises: 77e5eb8019bf
Create Date: 2026-09-26 15:06:40.190928

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


revision: str = '1442e094f138'
down_revision: Union[str, None] = '77e5eb8019bf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('places', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('google_place_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True)
        )
        batch_op.create_index(batch_op.f('ix_places_google_place_id'), ['google_place_id'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('places', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_places_google_place_id'))
        batch_op.drop_column('google_place_id')

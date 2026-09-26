"""add places table + events.place_id + place favorite type

Revision ID: c8a15d07cecd
Revises: 7e15486bd51c
Create Date: 2026-09-26 13:50:14.187441

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


revision: str = 'c8a15d07cecd'
down_revision: Union[str, None] = '7e15486bd51c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


OLD_FAVORITE_TYPES = ('event', 'restaurant')
NEW_FAVORITE_TYPES = ('event', 'restaurant', 'place')


def upgrade() -> None:
    op.create_table(
        'places',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('address', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('image_url', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('source', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('external_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('created_at', sqlmodel.sql.sqltypes.UTCDateTime(), nullable=False),
        sa.Column('updated_at', sqlmodel.sql.sqltypes.UTCDateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_places_external_id'), 'places', ['external_id'], unique=False)
    op.create_index(op.f('ix_places_name'), 'places', ['name'], unique=False)
    op.create_index(op.f('ix_places_source'), 'places', ['source'], unique=False)

    # events.place_id → FK to places(id)
    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.add_column(sa.Column('place_id', sa.Integer(), nullable=True))
        batch_op.create_index(batch_op.f('ix_events_place_id'), ['place_id'], unique=False)
        batch_op.create_foreign_key(
            'fk_events_place_id_places',
            'places',
            ['place_id'],
            ['id'],
        )

    # Extend FavoriteItemType enum with 'place'. Postgres has a native enum
    # type — ALTER TYPE is the only in-place way. SQLite emulates via CHECK
    # so we do a batch-recreate of the column.
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        op.execute("ALTER TYPE favoriteitemtype ADD VALUE IF NOT EXISTS 'place'")
    else:
        with op.batch_alter_table('favorites', schema=None) as batch_op:
            batch_op.alter_column(
                'item_type',
                existing_type=sa.Enum(*OLD_FAVORITE_TYPES, name='favoriteitemtype'),
                type_=sa.Enum(*NEW_FAVORITE_TYPES, name='favoriteitemtype'),
                existing_nullable=False,
            )


def downgrade() -> None:
    # Downgrade path for the enum on Postgres is intentionally partial —
    # PostgreSQL doesn't support removing values from an enum, so we leave
    # 'place' in the enum. Callers wanting a truly clean rollback should
    # `DROP TYPE favoriteitemtype CASCADE` and recreate manually.
    bind = op.get_bind()
    if bind.dialect.name != 'postgresql':
        with op.batch_alter_table('favorites', schema=None) as batch_op:
            batch_op.alter_column(
                'item_type',
                existing_type=sa.Enum(*NEW_FAVORITE_TYPES, name='favoriteitemtype'),
                type_=sa.Enum(*OLD_FAVORITE_TYPES, name='favoriteitemtype'),
                existing_nullable=False,
            )

    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.drop_constraint('fk_events_place_id_places', type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_events_place_id'))
        batch_op.drop_column('place_id')

    op.drop_index(op.f('ix_places_source'), table_name='places')
    op.drop_index(op.f('ix_places_name'), table_name='places')
    op.drop_index(op.f('ix_places_external_id'), table_name='places')
    op.drop_table('places')

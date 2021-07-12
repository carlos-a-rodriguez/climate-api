"""initial migration

Revision ID: cfd26d85f84c
Revises: 
Create Date: 2021-07-11 21:52:48.979013

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cfd26d85f84c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """ create the records table """
    op.create_table('records',
    sa.Column('record_id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.Float(), nullable=False),
    sa.Column('temperature', sa.Float(), nullable=False),
    sa.Column('humidity', sa.Float(), nullable=False),
    sa.CheckConstraint('humidity >= 0 AND humidity <= 100', name=op.f('ck_records_humidity')),
    sa.CheckConstraint('temperature >= -100 AND temperature <= 100', name=op.f('ck_records_temperature')),
    sa.PrimaryKeyConstraint('record_id', name=op.f('pk_records')),
    sa.UniqueConstraint('timestamp', name=op.f('uq_records_timestamp'))
    )


def downgrade():
    """ drop records table """
    op.drop_table('records')

"""remove temperature constraint

Revision ID: 73c55c9a1a55
Revises: a15003ec9054
Create Date: 2021-08-23 17:14:13.172194

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '73c55c9a1a55'
down_revision = 'a15003ec9054'
branch_labels = None
depends_on = None


def upgrade():
    """ drop temperature constraint """
    op.drop_constraint(op.f('ck_records_temperature'), table_name='records')


def downgrade():
    """ re-add temperature constraint """
    op.create_check_constraint(
        op.f('ck_records_temperature'),
        table_name='records',
        condition='temperature >= -100 AND temperature <= 100',
    )

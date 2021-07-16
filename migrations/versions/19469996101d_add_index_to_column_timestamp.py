"""add index to column timestamp

Revision ID: 19469996101d
Revises: cfd26d85f84c
Create Date: 2021-07-16 18:16:20.788335

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "19469996101d"
down_revision = "cfd26d85f84c"
branch_labels = None
depends_on = None


def upgrade():
    """ add a unique index to the timestamp column """
    with op.batch_alter_table("records") as batch_op:
        batch_op.drop_constraint("uq_records_timestamp", type_="unique")
        batch_op.create_index(op.f("ix_records_timestamp"), ["timestamp"], unique=True)


def downgrade():
    """ drop the unique index from the column timestamp """
    with op.batch_alter_table("records") as batch_op:
        batch_op.drop_index(op.f("ix_records_timestamp"))
        batch_op.create_unique_constraint("uq_records_timestamp", ["timestamp"])

"""Add profile_photo to User

Revision ID: 76df120774d0
Revises: b40a13529b75
Create Date: 2024-07-02 00:09:26.751509

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '76df120774d0'
down_revision = 'b40a13529b75'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('profile_photo', sa.String(length=120), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('profile_photo')

    # ### end Alembic commands ###
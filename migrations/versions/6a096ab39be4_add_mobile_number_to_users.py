"""add mobile_number to users

Revision ID: 6a096ab39be4
Revises: b23d058c4af8
Create Date: 2024-07-27 14:46:52.449122

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6a096ab39be4'
down_revision = 'b23d058c4af8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('mobile_number', sa.String(length=15), nullable=True))
        batch_op.drop_column('profile_photo_url')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('profile_photo_url', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
        batch_op.drop_column('mobile_number')

    # ### end Alembic commands ###

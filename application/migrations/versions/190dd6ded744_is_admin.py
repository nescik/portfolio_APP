"""is_admin

Revision ID: 190dd6ded744
Revises: f266e94c28d6
Create Date: 2022-01-16 15:58:07.016983

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '190dd6ded744'
down_revision = 'f266e94c28d6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('is_admin', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'is_admin')
    # ### end Alembic commands ###

"""rename

Revision ID: cbdaac3a7987
Revises: 6bd245e09ff0
Create Date: 2022-01-07 16:14:50.962969

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'cbdaac3a7987'
down_revision = '6bd245e09ff0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('rating', sa.Column('rating', sa.Integer(), nullable=True))
    op.drop_column('rating', 'ratings')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('rating', sa.Column('ratings', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.drop_column('rating', 'rating')
    # ### end Alembic commands ###
"""empty message

Revision ID: 69cd1a38b8ba
Revises: 8f974cc0ae47
Create Date: 2020-02-10 19:51:37.051325

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '69cd1a38b8ba'
down_revision = '8f974cc0ae47'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('dishes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('dishname', sa.String(length=50), nullable=True),
    sa.Column('amount', sa.Integer(), nullable=True),
    sa.Column('timetaken', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dishes_dishname'), 'dishes', ['dishname'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_dishes_dishname'), table_name='dishes')
    op.drop_table('dishes')
    # ### end Alembic commands ###

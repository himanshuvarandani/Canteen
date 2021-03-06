"""empty message

Revision ID: 8b693e40f871
Revises: ebc3553dbab4
Create Date: 2020-03-01 15:19:35.623061

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8b693e40f871'
down_revision = 'ebc3553dbab4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('recent_orders',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('history', sa.Column('recent_order_id', sa.Integer(), nullable=True))
    op.add_column('history', sa.Column('status', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'history', 'recent_orders', ['recent_order_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'history', type_='foreignkey')
    op.drop_column('history', 'status')
    op.drop_column('history', 'recent_order_id')
    op.drop_table('recent_orders')
    # ### end Alembic commands ###

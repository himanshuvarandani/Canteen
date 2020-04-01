"""empty message

Revision ID: 75ebae8e0d7d
Revises: 92754d9fc1a5
Create Date: 2020-03-23 14:16:24.657681

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '75ebae8e0d7d'
down_revision = '92754d9fc1a5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('history', sa.Column('removed_dish', sa.String(length=50), nullable=True))
    op.create_foreign_key(None, 'history', 'recent_orders', ['recent_order_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'history', type_='foreignkey')
    op.drop_column('history', 'removed_dish')
    # ### end Alembic commands ###
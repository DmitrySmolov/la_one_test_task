"""Initial migration.

Revision ID: bf83e21e3036
Revises: 
Create Date: 2024-03-12 21:17:38.533997

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bf83e21e3036'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('wb_products',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('notification_subscriptions',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('tg_user_id', sa.Integer(), nullable=False),
    sa.Column('wb_product_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['wb_product_id'], ['wb_products.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('tg_user_id', 'wb_product_id', name='unique_user_product')
    )
    op.create_index(op.f('ix_notification_subscriptions_created_at'), 'notification_subscriptions', ['created_at'], unique=False)
    op.create_index(op.f('ix_notification_subscriptions_tg_user_id'), 'notification_subscriptions', ['tg_user_id'], unique=False)
    op.create_index(op.f('ix_notification_subscriptions_wb_product_id'), 'notification_subscriptions', ['wb_product_id'], unique=False)
    op.create_table('wb_product_cards',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('wb_product_id', sa.Integer(), nullable=False),
    sa.Column('unit_price', sa.Integer(), nullable=False),
    sa.Column('sale_price', sa.Integer(), nullable=False),
    sa.Column('rating', sa.SmallInteger(), nullable=False),
    sa.Column('stock', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['wb_product_id'], ['wb_products.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_wb_product_cards_created_at'), 'wb_product_cards', ['created_at'], unique=False)
    op.create_index(op.f('ix_wb_product_cards_wb_product_id'), 'wb_product_cards', ['wb_product_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_wb_product_cards_wb_product_id'), table_name='wb_product_cards')
    op.drop_index(op.f('ix_wb_product_cards_created_at'), table_name='wb_product_cards')
    op.drop_table('wb_product_cards')
    op.drop_index(op.f('ix_notification_subscriptions_wb_product_id'), table_name='notification_subscriptions')
    op.drop_index(op.f('ix_notification_subscriptions_tg_user_id'), table_name='notification_subscriptions')
    op.drop_index(op.f('ix_notification_subscriptions_created_at'), table_name='notification_subscriptions')
    op.drop_table('notification_subscriptions')
    op.drop_table('wb_products')
    # ### end Alembic commands ###
